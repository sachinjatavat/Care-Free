from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.api.state import global_state

router = APIRouter(prefix="/api", tags=["Dashboard"])

@router.get("/dashboard")
def get_dashboard_data(db: Session = Depends(get_db)):
    sim = global_state.active_simulator
    res = global_state.latest_results

    if not sim or not res:
        res = global_state.initialize_default_simulation()
        sim = global_state.active_simulator

    bed_mgr = sim.bed_manager
    queue_mgr = sim.queue_manager

    occ = bed_mgr.get_occupied_counts()
    avail = bed_mgr.get_available_counts()
    total_beds = 45
    total_occupied = sum(occ.values())
    total_available = sum(avail.values())

    waiting_patients = queue_mgr.get_waiting_patients(sim.current_time)
    waiting_count = len(waiting_patients)
    critical_waiting = sum(1 for p in waiting_patients if p.acuity == 3)
    rejected_count = res.get("rejected", 0)

    recent_decisions = res.get("decisions", [])[-10:]
    recent_decisions.reverse()

    return {
        "total_beds": total_beds,
        "occupied": total_occupied,
        "available": total_available,
        "waiting": waiting_count,
        "rejected": rejected_count,
        "critical_waiting": critical_waiting,

        "general_total": 30,
        "general_occupied": occ["general"],
        "general_available": avail["general"],

        "monitored_total": 10,
        "monitored_occupied": occ["monitored"],
        "monitored_available": avail["monitored"],

        "critical_total": 5,
        "critical_occupied": occ["critical"],
        "critical_available": avail["critical"],

        "recent_decisions": recent_decisions
    }
