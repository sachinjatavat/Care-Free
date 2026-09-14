from typing import List, Optional
from pydantic import BaseModel, ConfigDict

class PatientBase(BaseModel):
    patient_id: str
    patient_name: str = "Anonymous Patient"
    arrival_time: float
    acuity: int
    acuity_weight: int
    required_bed_type: str
    compatible_bed_types: List[str]
    waiting_time: float = 0.0
    status: str = "WAITING"
    assigned_bed_id: Optional[str] = None
    admission_time: Optional[float] = None
    discharge_time: Optional[float] = None

class PatientCreate(PatientBase):
    realized_los: float

class PatientRead(PatientBase):
    realized_los: Optional[float] = None
    priority_score: float = 0.0
    recommended_bed_type: Optional[str] = None
    recommended_bed_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
