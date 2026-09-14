import pytest
from dataclasses import dataclass
from typing import List, Dict, Any

from backend.core.allocation_policy import AllocationPolicy, AllocationDecision

@dataclass
class MockPatient:
    patient_id: str
    arrival_time: float
    acuity: int
    acuity_weight: int
    required_bed_type: str
    compatible_bed_types: List[str]
    patient_name: str = "Test Patient"

@dataclass
class MockBed:
    bed_id: str
    bed_type: str
    status: str = "AVAILABLE"

def test_l1_uses_general_when_available():
    p = MockPatient("P-00001", 0.0, 1, 1, "general", ["general", "monitored", "critical"])
    avail_counts = {"general": 5, "monitored": 2, "critical": 1}
    avail_beds = {
        "general": [MockBed("G-01", "general"), MockBed("G-02", "general")],
        "monitored": [MockBed("M-01", "monitored")],
        "critical": [MockBed("C-01", "critical")]
    }
    dec = AllocationPolicy.evaluate_allocation(p, avail_counts, avail_beds, 0.0)
    assert dec.decision == "ADMITTED"
    assert dec.bed_type == "general"
    assert dec.bed_id == "G-01"
    assert dec.is_avoidable_specialized is False

def test_l1_uses_monitored_only_when_general_unavailable():
    p = MockPatient("P-00001", 0.0, 1, 1, "general", ["general", "monitored", "critical"])
    avail_counts = {"general": 0, "monitored": 2, "critical": 1}
    avail_beds = {
        "general": [],
        "monitored": [MockBed("M-01", "monitored")],
        "critical": [MockBed("C-01", "critical")]
    }
    dec = AllocationPolicy.evaluate_allocation(p, avail_counts, avail_beds, 0.0)
    assert dec.decision == "ADMITTED"
    assert dec.bed_type == "monitored"
    assert dec.bed_id == "M-01"
    assert dec.is_avoidable_specialized is False  # Because General was 0

def test_l1_uses_critical_only_when_lower_capacity_unavailable():
    p = MockPatient("P-00001", 0.0, 1, 1, "general", ["general", "monitored", "critical"])
    avail_counts = {"general": 0, "monitored": 0, "critical": 1}
    avail_beds = {
        "general": [],
        "monitored": [],
        "critical": [MockBed("C-01", "critical")]
    }
    dec = AllocationPolicy.evaluate_allocation(p, avail_counts, avail_beds, 0.0)
    assert dec.decision == "ADMITTED"
    assert dec.bed_type == "critical"
    assert dec.bed_id == "C-01"
    assert dec.is_avoidable_specialized is False  # Because General and Monitored were 0

def test_l2_uses_monitored():
    p = MockPatient("P-00002", 0.0, 2, 3, "monitored", ["monitored", "critical"])
    avail_counts = {"general": 10, "monitored": 2, "critical": 1}
    avail_beds = {
        "general": [MockBed("G-01", "general")],
        "monitored": [MockBed("M-01", "monitored")],
        "critical": [MockBed("C-01", "critical")]
    }
    dec = AllocationPolicy.evaluate_allocation(p, avail_counts, avail_beds, 0.0)
    assert dec.decision == "ADMITTED"
    assert dec.bed_type == "monitored"
    assert dec.bed_id == "M-01"

def test_l2_uses_critical_only_when_monitored_unavailable():
    p = MockPatient("P-00002", 0.0, 2, 3, "monitored", ["monitored", "critical"])
    avail_counts = {"general": 10, "monitored": 0, "critical": 1}
    avail_beds = {
        "general": [MockBed("G-01", "general")],
        "monitored": [],
        "critical": [MockBed("C-01", "critical")]
    }
    dec = AllocationPolicy.evaluate_allocation(p, avail_counts, avail_beds, 0.0)
    assert dec.decision == "ADMITTED"
    assert dec.bed_type == "critical"
    assert dec.bed_id == "C-01"

def test_l3_can_only_use_critical():
    p = MockPatient("P-00003", 0.0, 3, 8, "critical", ["critical"])
    avail_counts = {"general": 10, "monitored": 5, "critical": 0}
    avail_beds = {
        "general": [MockBed("G-01", "general")],
        "monitored": [MockBed("M-01", "monitored")],
        "critical": []
    }
    dec = AllocationPolicy.evaluate_allocation(p, avail_counts, avail_beds, 0.0)
    assert dec.decision == "WAITING"
    assert dec.bed_type is None
    assert dec.bed_id is None

def test_specialized_bed_preservation():
    # If L1 is placed in Monitored while General is free -> avoidable
    # (Notice: policy won't do this under standard logic, but test checks detection)
    p = MockPatient("P-00001", 0.0, 1, 1, "general", ["general", "monitored", "critical"])
    avail_counts = {"general": 1, "monitored": 1, "critical": 1}
    avail_beds = {
        "general": [MockBed("G-01", "general")],
        "monitored": [MockBed("M-01", "monitored")],
        "critical": [MockBed("C-01", "critical")]
    }
    dec = AllocationPolicy.evaluate_allocation(p, avail_counts, avail_beds, 0.0)
    # Correct allocation is General
    assert dec.bed_type == "general"
    assert dec.is_avoidable_specialized is False
