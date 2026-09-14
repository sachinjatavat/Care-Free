from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import csv
import io

from backend.api.state import global_state
from backend.core.allocation_policy import AllocationPolicy

router = APIRouter(prefix="/api", tags=["Decisions & Allocation"])

class AllocationDecisionRequest(BaseModel):
    patient_id: str

@router.get("/decisions")
def get_decisions(patient_id: Optional[str] = None):
    sim = global_state.active_simulator
    res = global_state.latest_results
    if not sim or not res:
        res = global_state.initialize_default_simulation()
        sim = global_state.active_simulator

    decisions = res.get("decisions", [])
    if patient_id:
        decisions = [d for d in decisions if d["patient_id"] == patient_id]

    return decisions

@router.get("/decisions/{patient_id}")
def get_decisions_for_patient(patient_id: str):
    sim = global_state.active_simulator
    res = global_state.latest_results
    if not sim or not res:
        res = global_state.initialize_default_simulation()
        sim = global_state.active_simulator

    decisions = [d for d in res.get("decisions", []) if d["patient_id"] == patient_id]
    if not decisions:
        raise HTTPException(status_code=404, detail=f"No decisions found for patient {patient_id}.")
    return decisions

@router.get("/export/decisions")
def export_decisions_csv():
    sim = global_state.active_simulator
    res = global_state.latest_results
    if not sim or not res:
        res = global_state.initialize_default_simulation()
        sim = global_state.active_simulator

    decisions = res.get("decisions", [])

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Timestamp", "PatientID", "PatientName", "Acuity", "AcuityWeight", "WaitingTime",
        "PriorityScore", "Decision", "BedType", "BedID", "Reason",
        "AvailableGeneral", "AvailableMonitored", "AvailableCritical"
    ])

    for d in decisions:
        writer.writerow([
            d.get("timestamp"), d.get("patient_id"), d.get("patient_name", f"Patient {d.get('patient_id')}"), d.get("acuity"), d.get("acuity_weight"),
            d.get("waiting_time"), d.get("priority_score"), d.get("decision"),
            d.get("bed_type"), d.get("bed_id"), d.get("reason"),
            d.get("available_general"), d.get("available_monitored"), d.get("available_critical")
        ])

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=CareFlow_Decisions_Audit_Log.csv"}
    )

@router.post("/allocation/decision")
def make_allocation_decision(req: AllocationDecisionRequest):
    sim = global_state.active_simulator
    if not sim:
        global_state.initialize_default_simulation()
        sim = global_state.active_simulator

    patient = sim.queue_manager.get_patient(req.patient_id)
    if not patient:
        # Create synthetic patient state if patient was not pre-existing in simulator queue
        next_idx = len(sim.queue_manager.all_patients) + 1
        patient_name = generate_patient_name(next_idx)
        acuity = 2
        req_bed = sim.REQUIRED_BED_TYPES[acuity]
        comp_beds = sim.COMPATIBLE_BED_TYPES[acuity]
        median = sim.MEDIAN_LOS[req_bed]
        mu = float(np.log(median))
        realized_los = float(sim.rng.lognormal(mean=mu, sigma=0.35))
        patient = PatientState(
            patient_id=req.patient_id,
            patient_name=patient_name,
            arrival_time=sim.current_time,
            acuity=acuity,
            acuity_weight=sim.ACUITY_WEIGHTS[acuity],
            required_bed_type=req_bed,
            compatible_bed_types=comp_beds,
            realized_los=realized_los,
            status="WAITING"
        )
        sim.queue_manager.add_patient(patient)

    wait_time = max(0.0, sim.current_time - patient.arrival_time) if patient.status == "WAITING" else patient.waiting_time
    score = AllocationPolicy.calculate_priority(patient.acuity, wait_time)

    avail_counts = sim.bed_manager.get_available_counts()
    avail_beds_map = {
        "general": sim.bed_manager.get_available_beds_by_type("general"),
        "monitored": sim.bed_manager.get_available_beds_by_type("monitored"),
        "critical": sim.bed_manager.get_available_beds_by_type("critical")
    }

    eval_dec = AllocationPolicy.evaluate_allocation(
        patient, avail_counts, avail_beds_map, sim.current_time
    )

    # For explicit manual allocation requests, if primary ward is full, allow overflow placement across any open bed
    if eval_dec.decision != "ADMITTED":
        manual_prefs = {
            3: ["critical", "monitored", "general"],
            2: ["monitored", "critical", "general"],
            1: ["general", "monitored", "critical"]
        }.get(patient.acuity, ["general", "monitored", "critical"])

        for btype in manual_prefs:
            if avail_counts.get(btype, 0) > 0 and avail_beds_map.get(btype):
                beds_of_type = sorted(avail_beds_map[btype], key=lambda b: b.bed_id)
                assigned_bed_id = beds_of_type[0].bed_id
                eval_dec = AllocationDecision(
                    patient_id=patient.patient_id,
                    acuity=patient.acuity,
                    acuity_weight=patient.acuity_weight,
                    waiting_time=wait_time,
                    priority_score=score,
                    decision="ADMITTED",
                    bed_type=btype,
                    bed_id=assigned_bed_id,
                    reason=f"Manual clinician allocation: Assigned to {btype.capitalize()} bed {assigned_bed_id}.",
                    is_avoidable_specialized=True
                )
                break

    if eval_dec.decision == "ADMITTED" and eval_dec.bed_id:
        exp_release = sim.current_time + (patient.realized_los if hasattr(patient, 'realized_los') and patient.realized_los else 120.0)
        sim.bed_manager.allocate_bed(
            eval_dec.bed_id, patient.patient_id, sim.current_time, exp_release
        )
        patient.status = "ADMITTED"
        patient.assigned_bed_id = eval_dec.bed_id
        patient.admission_time = sim.current_time
        patient.waiting_time = wait_time
        sim.queue_manager.remove_from_waiting(patient.patient_id)
        sim._record_decision(eval_dec, sim.current_time)

    return {
        "patient_id": patient.patient_id,
        "patient_name": getattr(patient, "patient_name", f"Patient {patient.patient_id}"),
        "acuity": patient.acuity,
        "waiting_time": round(wait_time, 2),
        "priority_score": round(score, 2),
        "required_bed": patient.required_bed_type,
        "compatible_beds": patient.compatible_bed_types,
        "available_capacity": avail_counts,
        "recommended_bed_type": eval_dec.bed_type,
        "recommended_bed_id": eval_dec.bed_id,
        "decision": eval_dec.decision,
        "reason": eval_dec.reason
    }
