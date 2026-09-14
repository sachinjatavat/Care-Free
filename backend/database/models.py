import json
from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime, func
from backend.database.database import Base

class PatientModel(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String, unique=True, index=True)
    patient_name = Column(String, default="Anonymous Patient")
    arrival_time = Column(Float)
    acuity = Column(Integer)
    acuity_weight = Column(Integer)
    required_bed_type = Column(String)
    compatible_bed_types_json = Column(Text)
    waiting_time = Column(Float, default=0.0)
    status = Column(String, default="WAITING")
    assigned_bed_id = Column(String, nullable=True)
    admission_time = Column(Float, nullable=True)
    discharge_time = Column(Float, nullable=True)
    realized_los = Column(Float, nullable=True)

    @property
    def compatible_bed_types(self):
        if self.compatible_bed_types_json:
            return json.loads(self.compatible_bed_types_json)
        return []

    @compatible_bed_types.setter
    def compatible_bed_types(self, value):
        self.compatible_bed_types_json = json.dumps(value)


class BedModel(Base):
    __tablename__ = "beds"

    id = Column(Integer, primary_key=True, index=True)
    bed_id = Column(String, unique=True, index=True)
    bed_type = Column(String, index=True)
    status = Column(String, default="AVAILABLE")
    patient_id = Column(String, nullable=True)
    admission_time = Column(Float, nullable=True)
    expected_release_time = Column(Float, nullable=True)


class EventModel(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(Float, index=True)
    event_type = Column(String)
    patient_id = Column(String)
    details_json = Column(Text, nullable=True)


class DecisionModel(Base):
    __tablename__ = "decisions"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(Float, index=True)
    patient_id = Column(String, index=True)
    acuity = Column(Integer)
    acuity_weight = Column(Integer)
    waiting_time = Column(Float)
    priority_score = Column(Float)
    decision = Column(String)
    bed_type = Column(String, nullable=True)
    bed_id = Column(String, nullable=True)
    reason = Column(String)
    available_general = Column(Integer)
    available_monitored = Column(Integer)
    available_critical = Column(Integer)


class SimulationRunModel(Base):
    __tablename__ = "simulation_runs"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, unique=True, index=True)
    seed = Column(Integer)
    total_arrivals = Column(Integer)
    admitted = Column(Integer)
    rejected = Column(Integer)
    average_wait = Column(Float)
    weighted_wait_utility = Column(Float)
    critical_wait_utility = Column(Float)
    rejection_utility = Column(Float)
    specialized_capacity_utility = Column(Float)
    overall_score = Column(Float)
    runtime_seconds = Column(Float)
    created_at = Column(DateTime, default=func.now())


class MetricsModel(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, ForeignKey("simulation_runs.run_id"))
    metric_name = Column(String)
    metric_value = Column(Float)
