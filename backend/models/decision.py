from typing import Optional
from pydantic import BaseModel, ConfigDict

class DecisionBase(BaseModel):
    timestamp: float
    patient_id: str
    acuity: int
    acuity_weight: int
    waiting_time: float
    priority_score: float
    decision: str
    bed_type: Optional[str] = None
    bed_id: Optional[str] = None
    reason: str
    available_general: int
    available_monitored: int
    available_critical: int

class DecisionRead(DecisionBase):
    id: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)
