import pytest
from dataclasses import dataclass
from backend.core.metrics import CompetitionMetrics

@dataclass
class DummyPatient:
    acuity: int
    acuity_weight: int
    waiting_time: float
    status: str

def test_metrics_formulas():
    patients = [
        DummyPatient(acuity=1, acuity_weight=1, waiting_time=10.0, status="ADMITTED"),
        DummyPatient(acuity=2, acuity_weight=3, waiting_time=20.0, status="ADMITTED"),
        DummyPatient(acuity=3, acuity_weight=8, waiting_time=5.0, status="ADMITTED"),
        DummyPatient(acuity=1, acuity_weight=1, waiting_time=245.0, status="REJECTED")
    ]

    metrics = CompetitionMetrics.calculate_metrics(
        patients=patients,
        avoidable_specialized_count=0,
        runtime_seconds=1.2,
        total_cohort_size=500
    )

    assert 0.0 <= metrics["weighted_wait_utility"] <= 1.0
    assert 0.0 <= metrics["critical_wait_utility"] <= 1.0
    assert 0.0 <= metrics["rejection_utility"] <= 1.0
    assert metrics["specialized_capacity_utility"] == 1.0
    assert metrics["overall_score"] > 0.0
