import random
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

router = APIRouter(prefix="/api/ambulance", tags=["Ambulance Emergency System"])

class DispatchRequest(BaseModel):
    patient_name: str = Field(..., description="Full Name of Patient")
    contact_number: str = Field(..., description="Emergency Contact Number")
    pickup_address: str = Field(..., description="Pickup Location Address / GPS")
    triage_level: str = Field(..., description="CRITICAL, URGENT, or STANDARD")
    hospital_id: Optional[str] = Field(None, description="Target Hospital ID")

@router.post("/dispatch")
def dispatch_ambulance(req: DispatchRequest):
    dispatch_num = random.randint(1000, 9999)
    amb_num = random.randint(101, 199)
    drivers = [
        ("Rajesh Sharma", "+91-98765-43210"),
        ("Vikram Singh", "+91-98112-23344"),
        ("Amitabh Verma", "+91-98777-66554"),
        ("Suresh Kumar", "+91-99887-76655")
    ]
    driver = random.choice(drivers)
    eta = round(random.uniform(4.5, 9.0), 1)

    triage = req.triage_level.upper()
    equipment = "Advanced Life Support (ALS) Ventilator, Defibrillator, Cardiac Monitor, High-Flow O2"
    if triage == "STANDARD":
        equipment = "Basic Life Support (BLS) Oxygen, Stretcher, Vital Monitor, First Aid"

    return {
        "dispatch_id": f"SOS-AMB-{dispatch_num}",
        "status": "DISPATCHED_EN_ROUTE",
        "ambulance_code": f"AMB-{amb_num} (ALS Rapid Unit)",
        "driver_name": driver[0],
        "driver_phone": driver[1],
        "paramedic_lead": "Nurse Sarah Lin / Dr. Alex",
        "eta_minutes": eta,
        "triage_level": triage,
        "pickup_address": req.pickup_address,
        "target_hospital": req.hospital_id or "h-01",
        "equipment": equipment,
        "dispatch_timestamp": "Just Now"
    }
