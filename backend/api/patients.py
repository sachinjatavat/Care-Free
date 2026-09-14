import numpy as np
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from backend.api.state import global_state
from backend.core.queue_manager import PatientState
from backend.core.allocation_policy import AllocationPolicy

router = APIRouter(prefix="/api/patients", tags=["Patients"])

from backend.core.simulator import generate_patient_name

class SimulateArrivalRequest(BaseModel):
    acuity: int = Field(..., ge=1, le=3, description="Patient acuity level: 1, 2, or 3")
    patient_name: Optional[str] = Field(None, description="Optional patient full name")

@router.get("/waiting")
def get_waiting_patients():
    sim = global_state.active_simulator
    if not sim:
        global_state.initialize_default_simulation()
        sim = global_state.active_simulator

    waiting_list = sim.queue_manager.get_waiting_patients(sim.current_time)
    results = []

    avail_counts = sim.bed_manager.get_available_counts()
    avail_beds_map = {
        "general": sim.bed_manager.get_available_beds_by_type("general"),
        "monitored": sim.bed_manager.get_available_beds_by_type("monitored"),
        "critical": sim.bed_manager.get_available_beds_by_type("critical")
    }

    for p in waiting_list:
        wait_time = max(0.0, sim.current_time - p.arrival_time)
        score = AllocationPolicy.calculate_priority(p.acuity, wait_time)
        
        # Determine recommendation using policy
        eval_dec = AllocationPolicy.evaluate_allocation(
            p, avail_counts, avail_beds_map, sim.current_time
        )

        results.append({
            "patient_id": p.patient_id,
            "patient_name": getattr(p, "patient_name", f"Patient {p.patient_id}"),
            "arrival_time": round(p.arrival_time, 2),
            "acuity": p.acuity,
            "acuity_weight": p.acuity_weight,
            "waiting_time": round(wait_time, 2),
            "required_bed": p.required_bed_type,
            "compatible_beds": p.compatible_bed_types,
            "priority_score": round(score, 2),
            "recommended_bed_type": eval_dec.bed_type,
            "recommended_bed_id": eval_dec.bed_id,
            "status": p.status
        })

    # Sort by priority score DESC, then arrival_time ASC
    results.sort(key=lambda x: (-x["priority_score"], x["arrival_time"], x["patient_id"]))
    return results

@router.get("/{patient_id}")
def get_patient_detail(patient_id: str):
    sim = global_state.active_simulator
    if not sim:
        global_state.initialize_default_simulation()
        sim = global_state.active_simulator

    p = sim.queue_manager.get_patient(patient_id)
    if not p:
        raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found.")

    wait_time = p.waiting_time if p.status != "WAITING" else max(0.0, sim.current_time - p.arrival_time)
    score = AllocationPolicy.calculate_priority(p.acuity, wait_time)

    return {
        "patient_id": p.patient_id,
        "patient_name": getattr(p, "patient_name", f"Patient {p.patient_id}"),
        "arrival_time": round(p.arrival_time, 2),
        "acuity": p.acuity,
        "acuity_weight": p.acuity_weight,
        "required_bed_type": p.required_bed_type,
        "compatible_bed_types": p.compatible_bed_types,
        "waiting_time": round(wait_time, 2),
        "priority_score": round(score, 2),
        "status": p.status,
        "assigned_bed_id": p.assigned_bed_id,
        "admission_time": round(p.admission_time, 2) if p.admission_time else None,
        "discharge_time": round(p.discharge_time, 2) if p.discharge_time else None
    }

@router.post("/simulate-arrival")
def simulate_patient_arrival(req: SimulateArrivalRequest):
    sim = global_state.active_simulator
    if not sim:
        global_state.initialize_default_simulation()
        sim = global_state.active_simulator

    # Increment simulation time slightly for dynamic arrival
    sim.current_time += round(float(sim.rng.exponential(scale=2.5)), 2)
    next_idx = len(sim.queue_manager.all_patients) + 1
    patient_id = f"P-{next_idx:05d}"
    patient_name = req.patient_name or generate_patient_name(next_idx)

    acuity = req.acuity
    req_bed = sim.REQUIRED_BED_TYPES[acuity]
    comp_beds = sim.COMPATIBLE_BED_TYPES[acuity]
    median = sim.MEDIAN_LOS[req_bed]
    mu = float(np.log(median))
    realized_los = float(sim.rng.lognormal(mean=mu, sigma=0.35))

    patient = PatientState(
        patient_id=patient_id,
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

    # Evaluate allocation with backend authority
    avail_counts = sim.bed_manager.get_available_counts()
    avail_beds_map = {
        "general": sim.bed_manager.get_available_beds_by_type("general"),
        "monitored": sim.bed_manager.get_available_beds_by_type("monitored"),
        "critical": sim.bed_manager.get_available_beds_by_type("critical")
    }

    decision = AllocationPolicy.evaluate_allocation(
        patient, avail_counts, avail_beds_map, sim.current_time
    )

    if decision.decision == "ADMITTED" and decision.bed_id:
        exp_release = sim.current_time + patient.realized_los
        sim.bed_manager.allocate_bed(
            decision.bed_id, patient.patient_id, sim.current_time, exp_release
        )
        patient.status = "ADMITTED"
        patient.assigned_bed_id = decision.bed_id
        patient.admission_time = sim.current_time
        patient.waiting_time = 0.0
        sim.queue_manager.remove_from_waiting(patient.patient_id)
        sim._record_decision(decision, sim.current_time)
    else:
        sim._record_decision(decision, sim.current_time)

    return {
        "patient_id": patient_id,
        "patient_name": patient_name,
        "acuity": acuity,
        "arrival_time": round(sim.current_time, 2),
        "decision": decision.decision,
        "assigned_bed_id": decision.bed_id,
        "reason": decision.reason,
        "current_simulation_time": round(sim.current_time, 2)
    }
