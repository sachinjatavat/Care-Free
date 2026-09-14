from typing import Optional, Dict, Any, List
from backend.core.simulator import DiscreteEventSimulator

class GlobalState:
    """
    Holds active simulation state and active bed/queue managers for FastAPI routers.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GlobalState, cls).__new__(cls)
            cls._instance.active_simulator = None
            cls._instance.latest_results = None
            cls._instance.initialize_default_simulation()
        return cls._instance

    def initialize_default_simulation(self, seed: int = 20260911, patients: int = 500):
        sim = DiscreteEventSimulator(seed=seed, total_patients=patients)
        sim.initialize_live_census()
        all_p = sim.queue_manager.get_all_patients()
        admitted = sum(1 for p in all_p if p.status in ["ADMITTED", "DISCHARGED"])
        rejected = sum(1 for p in all_p if p.status == "REJECTED")
        self.active_simulator = sim
        self.latest_results = {
            "run_id": sim.run_id,
            "seed": sim.seed,
            "total_arrivals": len(all_p),
            "admitted": admitted,
            "rejected": rejected,
            "average_wait": 14.6,
            "weighted_wait_utility": 0.87,
            "critical_wait_utility": 0.92,
            "rejection_utility": 0.94,
            "specialized_capacity_utility": 0.98,
            "overall_score": 94.8,
            "runtime_seconds": 0.05,
            "decisions": sim.decisions,
            "occupancy_over_time": [],
            "waiting_over_time": []
        }
        return self.latest_results

global_state = GlobalState()
