from typing import Dict, List, Optional
from dataclasses import dataclass, field

@dataclass
class PatientState:
    patient_id: str
    patient_name: str
    arrival_time: float
    acuity: int
    acuity_weight: int
    required_bed_type: str
    compatible_bed_types: List[str]
    realized_los: float
    waiting_time: float = 0.0
    status: str = "WAITING"  # WAITING, ADMITTED, REJECTED, DISCHARGED
    assigned_bed_id: Optional[str] = None
    admission_time: Optional[float] = None
    discharge_time: Optional[float] = None

    def update_waiting_time(self, current_time: float):
        if self.status == "WAITING":
            self.waiting_time = max(0.0, current_time - self.arrival_time)

    def calculate_priority_score(self, current_time: float) -> float:
        self.update_waiting_time(current_time)
        return self.acuity_weight * min(self.waiting_time, 240.0)

class QueueManager:
    def __init__(self):
        self.all_patients: Dict[str, PatientState] = {}
        self.waiting_queue: List[str] = []  # List of patient_ids

    def reset(self):
        self.all_patients.clear()
        self.waiting_queue.clear()

    def add_patient(self, patient: PatientState):
        self.all_patients[patient.patient_id] = patient
        if patient.status == "WAITING":
            self.waiting_queue.append(patient.patient_id)

    def get_patient(self, patient_id: str) -> Optional[PatientState]:
        return self.all_patients.get(patient_id)

    def get_waiting_patients(self, current_time: float) -> List[PatientState]:
        waiting = []
        for pid in list(self.waiting_queue):
            p = self.all_patients.get(pid)
            if p and p.status == "WAITING":
                p.update_waiting_time(current_time)
                waiting.append(p)
        return waiting

    def remove_from_waiting(self, patient_id: str):
        if patient_id in self.waiting_queue:
            self.waiting_queue.remove(patient_id)

    def get_all_patients(self) -> List[PatientState]:
        return list(self.all_patients.values())
