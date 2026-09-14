from typing import Dict, List, Optional
from dataclasses import dataclass, field

@dataclass
class BedState:
    bed_id: str
    bed_type: str
    status: str = "AVAILABLE"  # AVAILABLE, OCCUPIED
    patient_id: Optional[str] = None
    admission_time: Optional[float] = None
    expected_release_time: Optional[float] = None

class BedManager:
    def __init__(self):
        self.beds: Dict[str, BedState] = {}
        self._initialize_beds()

    def _initialize_beds(self):
        self.beds.clear()
        # 30 General Care beds: G-01 to G-30
        for i in range(1, 31):
            bed_id = f"G-{i:02d}"
            self.beds[bed_id] = BedState(bed_id=bed_id, bed_type="general")

        # 10 Monitored / Step-Down beds: M-01 to M-10
        for i in range(1, 11):
            bed_id = f"M-{i:02d}"
            self.beds[bed_id] = BedState(bed_id=bed_id, bed_type="monitored")

        # 5 Critical Care (ICU) beds: C-01 to C-05
        for i in range(1, 6):
            bed_id = f"C-{i:02d}"
            self.beds[bed_id] = BedState(bed_id=bed_id, bed_type="critical")

    def reset(self):
        self._initialize_beds()

    def get_bed(self, bed_id: str) -> Optional[BedState]:
        return self.beds.get(bed_id)

    def get_all_beds(self) -> List[BedState]:
        return list(self.beds.values())

    def get_available_counts(self) -> Dict[str, int]:
        counts = {"general": 0, "monitored": 0, "critical": 0}
        for bed in self.beds.values():
            if bed.status == "AVAILABLE":
                counts[bed.bed_type] += 1
        return counts

    def get_occupied_counts(self) -> Dict[str, int]:
        counts = {"general": 0, "monitored": 0, "critical": 0}
        for bed in self.beds.values():
            if bed.status == "OCCUPIED":
                counts[bed.bed_type] += 1
        return counts

    def get_available_beds_by_type(self, bed_type: str) -> List[BedState]:
        return [
            bed for bed in self.beds.values()
            if bed.bed_type == bed_type and bed.status == "AVAILABLE"
        ]

    def allocate_bed(
        self,
        bed_id: str,
        patient_id: str,
        current_time: float,
        expected_release_time: Optional[float] = None
    ) -> BedState:
        bed = self.beds.get(bed_id)
        if not bed:
            raise ValueError(f"Bed {bed_id} does not exist.")
        if bed.status != "AVAILABLE":
            raise ValueError(f"Bed {bed_id} is already occupied by {bed.patient_id}.")

        bed.status = "OCCUPIED"
        bed.patient_id = patient_id
        bed.admission_time = current_time
        bed.expected_release_time = expected_release_time
        return bed

    def release_bed(self, bed_id: str) -> Optional[str]:
        bed = self.beds.get(bed_id)
        if not bed:
            return None
        patient_id = bed.patient_id
        bed.status = "AVAILABLE"
        bed.patient_id = None
        bed.admission_time = None
        bed.expected_release_time = None
        return patient_id

    def find_first_available_bed(self, bed_type: str) -> Optional[BedState]:
        avail = self.get_available_beds_by_type(bed_type)
        if avail:
            # Sort deterministically by bed_id
            avail.sort(key=lambda b: b.bed_id)
            return avail[0]
        return None
