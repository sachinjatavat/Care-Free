from dataclasses import dataclass, field
from typing import Any, Dict, Optional

class EventType:
    PATIENT_ARRIVAL = "PATIENT_ARRIVAL"
    PATIENT_DISCHARGE = "PATIENT_DISCHARGE"

@dataclass(order=True)
class Event:
    timestamp: float
    event_type: str = field(compare=False)
    patient_id: str = field(compare=False)
    data: Dict[str, Any] = field(default_factory=dict, compare=False)
