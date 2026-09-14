import pytest
from backend.core.simulator import DiscreteEventSimulator

def test_pcg64_seed_reproducibility():
    sim1 = DiscreteEventSimulator(seed=20260911, total_patients=100)
    res1 = sim1.run()

    sim2 = DiscreteEventSimulator(seed=20260911, total_patients=100)
    res2 = sim2.run()

    assert res1["admitted"] == res2["admitted"]
    assert res1["rejected"] == res2["rejected"]
    assert res1["average_wait"] == res2["average_wait"]
    assert res1["overall_score"] == res2["overall_score"]
    assert len(res1["decisions"]) == len(res2["decisions"])

def test_no_capacity_overflow_and_no_eviction():
    sim = DiscreteEventSimulator(seed=20260911, total_patients=500)
    res = sim.run()

    # Check that occupancy never exceeded bed bounds (30 Gen, 10 Mon, 5 Crit)
    for sample in res["occupancy_over_time"]:
        assert sample["general"] <= 30
        assert sample["monitored"] <= 10
        assert sample["critical"] <= 5
        assert sample["total"] <= 45

    # Check that patients admitted were never evicted (either ADMITTED or DISCHARGED)
    all_patients = res["patients"]
    for p in all_patients:
        if p.admission_time is not None:
            assert p.status in ["ADMITTED", "DISCHARGED"]
            assert p.status != "REJECTED"

def test_rejection_after_240_minutes():
    sim = DiscreteEventSimulator(seed=20260911, total_patients=500)
    res = sim.run()

    all_patients = res["patients"]
    rejected = [p for p in all_patients if p.status == "REJECTED"]
    for p in rejected:
        assert p.waiting_time >= 240.0
        assert p.assigned_bed_id is None

def test_decision_logs_contain_every_decision():
    sim = DiscreteEventSimulator(seed=20260911, total_patients=500)
    res = sim.run()

    decisions = res["decisions"]
    assert len(decisions) >= 500  # At least one decision per patient arrival
    for d in decisions:
        assert "timestamp" in d
        assert "patient_id" in d
        assert "decision" in d
        assert d["decision"] in ["ADMITTED", "WAITING", "REJECTED"]
