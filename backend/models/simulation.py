from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict

class SimulationRunRequest(BaseModel):
    seed: int = 20260911
    patients: int = 500

class SimulationRunResult(BaseModel):
    run_id: str
    seed: int
    total_arrivals: int
    admitted: int
    rejected: int
    average_wait: float
    weighted_wait_utility: float
    critical_wait_utility: float
    rejection_utility: float
    specialized_capacity_utility: float
    overall_score: float
    runtime_seconds: float

    model_config = ConfigDict(from_attributes=True)

class AnalyticsData(BaseModel):
    metrics: SimulationRunResult
    occupancy_over_time: List[Dict[str, Any]]
    waiting_over_time: List[Dict[str, Any]]
    admissions_by_acuity: Dict[str, int]
    average_wait_by_acuity: Dict[str, float]
    rejections_by_acuity: Dict[str, int]
    specialized_assignments: Dict[str, int]
