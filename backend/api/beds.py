from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from backend.api.state import global_state

router = APIRouter(prefix="/api/beds", tags=["Beds"])

@router.get("")
def get_all_beds():
    sim = global_state.active_simulator
    if not sim:
        global_state.initialize_default_simulation()
        sim = global_state.active_simulator

    beds = sim.bed_manager.get_all_beds()
    results = []
    for b in sorted(beds, key=lambda x: x.bed_id):
        p_name = None
        if b.patient_id:
            p = sim.queue_manager.get_patient(b.patient_id)
            if p:
                p_name = getattr(p, "patient_name", f"Patient {b.patient_id}")
        results.append({
            "bed_id": b.bed_id,
            "bed_type": b.bed_type,
            "status": b.status,
            "patient_id": b.patient_id,
            "patient_name": p_name,
            "admission_time": round(b.admission_time, 2) if b.admission_time else None,
            "expected_release_time": round(b.expected_release_time, 2) if b.expected_release_time else None
        })
    return results

@router.get("/{bed_id}")
def get_bed_detail(bed_id: str):
    sim = global_state.active_simulator
    if not sim:
        global_state.initialize_default_simulation()
        sim = global_state.active_simulator

    b = sim.bed_manager.get_bed(bed_id)
    if not b:
        raise HTTPException(status_code=404, detail=f"Bed {bed_id} not found.")

    p_name = None
    if b.patient_id:
        p = sim.queue_manager.get_patient(b.patient_id)
        if p:
            p_name = getattr(p, "patient_name", f"Patient {b.patient_id}")

    return {
        "bed_id": b.bed_id,
        "bed_type": b.bed_type,
        "status": b.status,
        "patient_id": b.patient_id,
        "patient_name": p_name,
        "admission_time": round(b.admission_time, 2) if b.admission_time else None,
        "expected_release_time": round(b.expected_release_time, 2) if b.expected_release_time else None
    }
