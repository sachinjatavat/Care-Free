from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.database import get_db
from backend.database.models import SimulationRunModel, MetricsModel
from backend.models.simulation import SimulationRunRequest, SimulationRunResult
from backend.api.state import global_state
from backend.core.simulator import DiscreteEventSimulator

router = APIRouter(prefix="/api/simulation", tags=["Simulation"])

@router.post("/run", response_model=SimulationRunResult)
def run_simulation(req: SimulationRunRequest, db: Session = Depends(get_db)):
    sim = DiscreteEventSimulator(seed=req.seed, total_patients=req.patients)
    results = sim.run()
    global_state.active_simulator = sim
    global_state.latest_results = results

    # Persist in SQLite
    run_entry = SimulationRunModel(
        run_id=results["run_id"],
        seed=results["seed"],
        total_arrivals=results["total_arrivals"],
        admitted=results["admitted"],
        rejected=results["rejected"],
        average_wait=results["average_wait"],
        weighted_wait_utility=results["weighted_wait_utility"],
        critical_wait_utility=results["critical_wait_utility"],
        rejection_utility=results["rejection_utility"],
        specialized_capacity_utility=results["specialized_capacity_utility"],
        overall_score=results["overall_score"],
        runtime_seconds=results["runtime_seconds"]
    )
    db.add(run_entry)
    db.commit()

    return SimulationRunResult(
        run_id=results["run_id"],
        seed=results["seed"],
        total_arrivals=results["total_arrivals"],
        admitted=results["admitted"],
        rejected=results["rejected"],
        average_wait=results["average_wait"],
        weighted_wait_utility=results["weighted_wait_utility"],
        critical_wait_utility=results["critical_wait_utility"],
        rejection_utility=results["rejection_utility"],
        specialized_capacity_utility=results["specialized_capacity_utility"],
        overall_score=results["overall_score"],
        runtime_seconds=results["runtime_seconds"]
    )

@router.get("/status")
def get_simulation_status():
    sim = global_state.active_simulator
    if not sim:
        return {"status": "IDLE", "current_time": 0.0}

    return {
        "status": "READY",
        "seed": sim.seed,
        "patients_total": sim.total_patients,
        "current_time": round(sim.current_time, 2),
        "run_id": sim.run_id
    }

@router.get("/results", response_model=SimulationRunResult)
def get_simulation_results():
    res = global_state.latest_results
    if not res:
        res = global_state.initialize_default_simulation()

    return SimulationRunResult(
        run_id=res["run_id"],
        seed=res["seed"],
        total_arrivals=res["total_arrivals"],
        admitted=res["admitted"],
        rejected=res["rejected"],
        average_wait=res["average_wait"],
        weighted_wait_utility=res["weighted_wait_utility"],
        critical_wait_utility=res["critical_wait_utility"],
        rejection_utility=res["rejection_utility"],
        specialized_capacity_utility=res["specialized_capacity_utility"],
        overall_score=res["overall_score"],
        runtime_seconds=res["runtime_seconds"]
    )
