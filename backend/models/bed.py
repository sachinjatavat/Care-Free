from typing import Optional
from pydantic import BaseModel, ConfigDict

class BedBase(BaseModel):
    bed_id: str
    bed_type: str
    status: str = "AVAILABLE"
    patient_id: Optional[str] = None
    admission_time: Optional[float] = None
    expected_release_time: Optional[float] = None

class BedRead(BedBase):
    model_config = ConfigDict(from_attributes=True)
