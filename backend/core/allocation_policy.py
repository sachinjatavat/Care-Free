from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass

@dataclass
class AllocationDecision:
    patient_id: str
    acuity: int
    acuity_weight: int
    waiting_time: float
    priority_score: float
    decision: str  # ADMITTED, WAITING, REJECTED
    bed_type: Optional[str]
    bed_id: Optional[str]
    reason: str
    is_avoidable_specialized: bool = False

class AllocationPolicy:
    """
    Online Bed Allocation Policy for CareFlow.
    Strictly isolated: evaluates decisions based ONLY on current simulation state.
    """

    ACUITY_WEIGHTS = {1: 1, 2: 3, 3: 8}
    
    # Bed type preferences per acuity level (ordered by preference)
    BED_PREFERENCES = {
        1: ["general", "monitored", "critical"],
        2: ["monitored", "critical"],
        3: ["critical"]
    }

    @staticmethod
    def calculate_priority(acuity: int, waiting_time: float) -> float:
        weight = AllocationPolicy.ACUITY_WEIGHTS.get(acuity, 1)
        capped_wait = min(max(0.0, waiting_time), 240.0)
        return weight * capped_wait

    @staticmethod
    def select_best_patient_for_bed(
        waiting_patients: List[Any],
        target_bed_type: str,
        current_time: float
    ) -> Optional[Any]:
        """
        Finds the highest priority compatible patient for a specific available bed_type.
        Tie-breaking: earlier arrival_time first, then lower patient_id.
        """
        compatible = []
        for p in waiting_patients:
            if target_bed_type in p.compatible_bed_types:
                wait_time = max(0.0, current_time - p.arrival_time)
                score = AllocationPolicy.calculate_priority(p.acuity, wait_time)
                compatible.append((score, p.arrival_time, p.patient_id, p))

        if not compatible:
            return None

        # Sort: Highest priority_score DESC, then arrival_time ASC, then patient_id ASC
        compatible.sort(key=lambda x: (-x[0], x[1], x[2]))
        return compatible[0][3]

    @staticmethod
    def evaluate_allocation(
        patient: Any,
        available_counts: Dict[str, int],
        available_beds: Dict[str, List[Any]],
        current_time: float
    ) -> AllocationDecision:
        """
        Evaluates the optimal bed assignment for a single revealed/waiting patient
        given current available bed capacities.
        """
        wait_time = max(0.0, current_time - patient.arrival_time)
        weight = AllocationPolicy.ACUITY_WEIGHTS.get(patient.acuity, 1)
        score = AllocationPolicy.calculate_priority(patient.acuity, wait_time)

        preferences = AllocationPolicy.BED_PREFERENCES.get(patient.acuity, [])
        assigned_bed_type = None
        assigned_bed_id = None
        avoidable_specialized = False

        for btype in preferences:
            if available_counts.get(btype, 0) > 0 and available_beds.get(btype):
                assigned_bed_type = btype
                # Sort available beds deterministically by bed_id
                beds_of_type = sorted(available_beds[btype], key=lambda b: b.bed_id)
                assigned_bed_id = beds_of_type[0].bed_id
                break

        if assigned_bed_type and assigned_bed_id:
            # Check for avoidable specialized bed assignment:
            # L1 -> Monitored while General was free
            # L1 -> Critical while General was free
            # L2 -> Critical while Monitored was free
            if patient.acuity == 1 and assigned_bed_type in ["monitored", "critical"] and available_counts.get("general", 0) > 0:
                avoidable_specialized = True
            elif patient.acuity == 2 and assigned_bed_type == "critical" and available_counts.get("monitored", 0) > 0:
                avoidable_specialized = True

            reason = f"Admitted to {assigned_bed_type.capitalize()} bed {assigned_bed_id} based on acuity L{patient.acuity} preference."
            if avoidable_specialized:
                reason += " [Avoidable specialized capacity assignment recorded]."

            return AllocationDecision(
                patient_id=patient.patient_id,
                acuity=patient.acuity,
                acuity_weight=weight,
                waiting_time=wait_time,
                priority_score=score,
                decision="ADMITTED",
                bed_type=assigned_bed_type,
                bed_id=assigned_bed_id,
                reason=reason,
                is_avoidable_specialized=avoidable_specialized
            )
        else:
            return AllocationDecision(
                patient_id=patient.patient_id,
                acuity=patient.acuity,
                acuity_weight=weight,
                waiting_time=wait_time,
                priority_score=score,
                decision="WAITING",
                bed_type=None,
                bed_id=None,
                reason=f"No compatible bed available for Acuity L{patient.acuity}. Enqueued in waiting roster."
            )
