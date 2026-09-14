import heapq
import time
import uuid
import numpy as np
from typing import Dict, List, Any, Optional

from backend.core.events import Event, EventType
from backend.core.bed_manager import BedManager
from backend.core.queue_manager import QueueManager, PatientState
from backend.core.allocation_policy import AllocationPolicy, AllocationDecision
from backend.core.metrics import CompetitionMetrics

FIRST_NAMES = ["Eleanor", "Marcus", "Sophia", "David", "Clara", "James", "Elena", "Arthur", "Chloe", "Julian", "Grace", "Oliver", "Maya", "Lucas", "Amara", "Gabriel", "Hannah", "Ethan", "Nora", "Caleb", "Zoe", "Leo", "Audrey", "Nathan", "Stella", "Owen"]
LAST_NAMES = ["Vance", "Thorne", "Sterling", "Kim", "Chen", "Reynolds", "Mercer", "Hayes", "Sinclair", "Bennett", "Cross", "Dalton", "Fletcher", "Gallagher", "Holloway", "Jennings", "Kovacs", "Lancaster", "Montgomery", "Navarro", "O'Connor", "Prescott"]

def generate_patient_name(idx: int) -> str:
    fn = FIRST_NAMES[idx % len(FIRST_NAMES)]
    ln = LAST_NAMES[(idx * 3) % len(LAST_NAMES)]
    return f"{fn} {ln}"

class DiscreteEventSimulator:
    """
    Event-Driven Hospital Bed Allocation Simulator using NumPy PCG64 Generator.
    """

    ACUITY_WEIGHTS = {1: 1, 2: 3, 3: 8}
    REQUIRED_BED_TYPES = {1: "general", 2: "monitored", 3: "critical"}
    COMPATIBLE_BED_TYPES = {
        1: ["general", "monitored", "critical"],
        2: ["monitored", "critical"],
        3: ["critical"]
    }
    MEDIAN_LOS = {
        "general": 120.0,
        "monitored": 180.0,
        "critical": 240.0
    }

    def __init__(self, seed: int = 20260911, total_patients: int = 500):
        self.seed = seed
        self.total_patients = total_patients
        self.rng = np.random.Generator(np.random.PCG64(self.seed))

        self.bed_manager = BedManager()
        self.queue_manager = QueueManager()

        self.event_queue: List[Event] = []
        self.current_time: float = 0.0

        self.decisions: List[Dict[str, Any]] = []
        self.avoidable_specialized_count: int = 0
        self.run_id: str = f"run_{uuid.uuid4().hex[:8]}"

        # Analytics telemetry over time
        self.occupancy_over_time: List[Dict[str, Any]] = []
        self.waiting_over_time: List[Dict[str, Any]] = []
        self.initialize_live_census()

    def initialize_live_census(self):
        """
        Initializes an active shift snapshot with 32 occupied beds and 7 waiting patients
        with full clinical telemetry details (names, acuities, scores).
        """
        self.bed_manager.reset()
        self.queue_manager.reset()
        self.event_queue.clear()
        self.decisions.clear()
        self.current_time = 30.0

        # Admitted patients occupying beds
        # 21 General Care beds (G-01 to G-21)
        gen_names = [
            "James Gordon", "Harvey Dent", "Rachel Dawes", "Lucius Fox", "Alfred Pennyworth",
            "Jim Gordon Jr", "Vicki Vale", "Thomas Wayne", "Martha Wayne", "Gillian Loeb",
            "Carmine Falcone", "Sal Maroni", "Rene Montoya", "Crispus Allen", "Arnold Flass",
            "Sarah Essen", "Hamilton Hill", "Gomez Addams", "Morticia Addams", "Lurch Addams", "Thing Addams"
        ]
        for i in range(1, 22):
            bed_id = f"G-{i:02d}"
            pid = f"P-003{i:02d}"
            pname = gen_names[i-1] if i-1 < len(gen_names) else generate_patient_name(300 + i)
            patient = PatientState(
                patient_id=pid, patient_name=pname, arrival_time=0.0, acuity=1,
                acuity_weight=1, required_bed_type="general", compatible_bed_types=["general", "monitored", "critical"],
                realized_los=120.0, status="ADMITTED", assigned_bed_id=bed_id, admission_time=0.0
            )
            self.queue_manager.add_patient(patient)
            self.bed_manager.allocate_bed(bed_id, pid, 0.0, 180.0)

        # 8 Monitored beds (M-01 to M-08)
        mon_names = [
            "Jonathan Crane", "Edward Nygma", "Oswald Cobblepot", "Victor Fries",
            "Waylon Jones", "Pamela Isley", "Harleen Quinzel", "Floyd Lawton"
        ]
        for i in range(1, 9):
            bed_id = f"M-{i:02d}"
            pid = f"P-0035{i:01d}"
            pname = mon_names[i-1]
            patient = PatientState(
                patient_id=pid, patient_name=pname, arrival_time=0.0, acuity=2,
                acuity_weight=3, required_bed_type="monitored", compatible_bed_types=["monitored", "critical"],
                realized_los=180.0, status="ADMITTED", assigned_bed_id=bed_id, admission_time=0.0
            )
            self.queue_manager.add_patient(patient)
            self.bed_manager.allocate_bed(bed_id, pid, 0.0, 240.0)

        # 3 Critical beds (C-01 to C-03)
        crit_names = ["Victor Zsasz", "Roman Sionis", "Julian Day"]
        for i in range(1, 4):
            bed_id = f"C-{i:02d}"
            pid = f"P-0039{i:01d}"
            pname = crit_names[i-1]
            patient = PatientState(
                patient_id=pid, patient_name=pname, arrival_time=0.0, acuity=3,
                acuity_weight=8, required_bed_type="critical", compatible_bed_types=["critical"],
                realized_los=240.0, status="ADMITTED", assigned_bed_id=bed_id, admission_time=0.0
            )
            self.queue_manager.add_patient(patient)
            self.bed_manager.allocate_bed(bed_id, pid, 0.0, 300.0)

        # 14 Waiting Patients
        initial_waiting = [
            ("P-00421", "Eleanor Vance", 12.0, 3, "critical", ["critical"]),
            ("P-00422", "Arthur Pendelton", 14.0, 2, "monitored", ["monitored", "critical"]),
            ("P-00423", "Clara Oswald", 17.0, 1, "general", ["general", "monitored", "critical"]),
            ("P-00424", "Marcus Brody", 20.0, 2, "monitored", ["monitored", "critical"]),
            ("P-00425", "Diana Prince", 25.0, 1, "general", ["general", "monitored", "critical"]),
            ("P-00426", "Bruce Wayne", 0.0, 3, "critical", ["critical"]),
            ("P-00427", "Selina Kyle", 28.0, 1, "general", ["general", "monitored", "critical"]),
            ("P-00428", "Victor Stone", 5.0, 2, "monitored", ["monitored", "critical"]),
            ("P-00429", "Barry Allen", 2.0, 1, "general", ["general", "monitored", "critical"]),
            ("P-00430", "Hal Jordan", 1.0, 3, "critical", ["critical"]),
            ("P-00431", "Oliver Queen", 8.0, 2, "monitored", ["monitored", "critical"]),
            ("P-00432", "Dinah Lance", 10.0, 1, "general", ["general", "monitored", "critical"]),
            ("P-00433", "Clark Kent", 15.0, 1, "general", ["general", "monitored", "critical"]),
            ("P-00434", "Lois Lane", 22.0, 2, "monitored", ["monitored", "critical"])
        ]

        for pid, pname, arr, acuity, req, comp in initial_waiting:
            patient = PatientState(
                patient_id=pid,
                patient_name=pname,
                arrival_time=arr,
                acuity=acuity,
                acuity_weight=self.ACUITY_WEIGHTS[acuity],
                required_bed_type=req,
                compatible_bed_types=comp,
                realized_los=self.MEDIAN_LOS[req],
                status="WAITING"
            )
            self.queue_manager.add_patient(patient)

        # Seed audit decision log
        self.decisions = [
            {"timestamp": 12.42, "patient_id": "P-00420", "patient_name": "James Gordon", "acuity": 3, "acuity_weight": 8, "waiting_time": 18.0, "priority_score": 144.0, "decision": "ADMITTED", "bed_type": "critical", "bed_id": "C-03", "reason": "Admitted to primary critical bed C-03", "available_general": 9, "available_monitored": 2, "available_critical": 2},
            {"timestamp": 12.35, "patient_id": "P-00419", "patient_name": "Harvey Dent", "acuity": 2, "acuity_weight": 3, "waiting_time": 16.0, "priority_score": 48.0, "decision": "ADMITTED", "bed_type": "monitored", "bed_id": "M-08", "reason": "Admitted to monitored bed M-08", "available_general": 9, "available_monitored": 2, "available_critical": 3},
            {"timestamp": 12.28, "patient_id": "P-00418", "patient_name": "Rachel Dawes", "acuity": 1, "acuity_weight": 1, "waiting_time": 22.0, "priority_score": 22.0, "decision": "ADMITTED", "bed_type": "general", "bed_id": "G-14", "reason": "Admitted to general bed G-14", "available_general": 9, "available_monitored": 3, "available_critical": 3},
            {"timestamp": 12.15, "patient_id": "P-00417", "patient_name": "Lucius Fox", "acuity": 1, "acuity_weight": 1, "waiting_time": 241.0, "priority_score": 241.0, "decision": "REJECTED", "bed_type": None, "bed_id": None, "reason": "Waiting time exceeded 240 minutes.", "available_general": 9, "available_monitored": 3, "available_critical": 3}
        ]

    def _generate_synthetic_patients(self) -> List[PatientState]:
        """
        Pre-generates patient arrival times, acuities, and realized LOS.
        The realized LOS is kept in PatientState but NOT passed to the Allocation Policy.
        """
        patients = []
        current_arrival = 0.0

        # Generate inter-arrival times: Exponential with mean 2.5 minutes
        inter_arrivals = self.rng.exponential(scale=2.5, size=self.total_patients)

        # Generate acuities according to specified probabilities
        acuities = self.rng.choice([1, 2, 3], p=[0.60, 0.30, 0.10], size=self.total_patients)

        for i in range(self.total_patients):
            if i > 0:
                current_arrival += float(inter_arrivals[i])
            else:
                current_arrival = 0.0

            acuity = int(acuities[i])
            req_bed = self.REQUIRED_BED_TYPES[acuity]
            comp_beds = self.COMPATIBLE_BED_TYPES[acuity]
            median = self.MEDIAN_LOS[req_bed]

            # Realized LOS ~ Lognormal(mu=ln(median), sigma=0.35)
            mu = float(np.log(median))
            realized_los = float(self.rng.lognormal(mean=mu, sigma=0.35))

            pid = f"P-{i+1:05d}"
            pname = generate_patient_name(i)

            patient = PatientState(
                patient_id=pid,
                patient_name=pname,
                arrival_time=current_arrival,
                acuity=acuity,
                acuity_weight=self.ACUITY_WEIGHTS[acuity],
                required_bed_type=req_bed,
                compatible_bed_types=comp_beds,
                realized_los=realized_los,
                status="WAITING"
            )
            patients.append(patient)

        return patients

    def _record_decision(self, decision: AllocationDecision, time_point: float):
        avail = self.bed_manager.get_available_counts()
        patient = self.queue_manager.get_patient(decision.patient_id)
        pname = patient.patient_name if patient else "Anonymous Patient"

        log_entry = {
            "timestamp": round(time_point, 2),
            "patient_id": decision.patient_id,
            "patient_name": pname,
            "acuity": decision.acuity,
            "acuity_weight": decision.acuity_weight,
            "waiting_time": round(decision.waiting_time, 2),
            "priority_score": round(decision.priority_score, 2),
            "decision": decision.decision,
            "bed_type": decision.bed_type,
            "bed_id": decision.bed_id,
            "reason": decision.reason,
            "available_general": avail["general"],
            "available_monitored": avail["monitored"],
            "available_critical": avail["critical"]
        }
        self.decisions.append(log_entry)
        if decision.is_avoidable_specialized:
            self.avoidable_specialized_count += 1

    def _check_and_reject_expired_waiting(self):
        """
        Rejects patients whose waiting time exceeds 240 minutes.
        """
        waiting_patients = self.queue_manager.get_waiting_patients(self.current_time)
        for p in waiting_patients:
            wait = self.current_time - p.arrival_time
            if wait > 240.0:
                p.status = "REJECTED"
                p.waiting_time = wait
                self.queue_manager.remove_from_waiting(p.patient_id)

                avail = self.bed_manager.get_available_counts()
                score = AllocationPolicy.calculate_priority(p.acuity, wait)

                self.decisions.append({
                    "timestamp": round(self.current_time, 2),
                    "patient_id": p.patient_id,
                    "acuity": p.acuity,
                    "acuity_weight": p.acuity_weight,
                    "waiting_time": round(wait, 2),
                    "priority_score": round(score, 2),
                    "decision": "REJECTED",
                    "bed_type": None,
                    "bed_id": None,
                    "reason": "Waiting time exceeded 240 minutes.",
                    "available_general": avail["general"],
                    "available_monitored": avail["monitored"],
                    "available_critical": avail["critical"]
                })

    def _attempt_allocations(self):
        """
        Scans waiting queue and allocates compatible capacity if available.
        """
        while True:
            allocated_any = False
            waiting_patients = self.queue_manager.get_waiting_patients(self.current_time)
            if not waiting_patients:
                break

            avail_counts = self.bed_manager.get_available_counts()
            avail_beds_map = {
                "general": self.bed_manager.get_available_beds_by_type("general"),
                "monitored": self.bed_manager.get_available_beds_by_type("monitored"),
                "critical": self.bed_manager.get_available_beds_by_type("critical")
            }

            # Check if any capacity exists
            total_avail = sum(avail_counts.values())
            if total_avail == 0:
                break

            # Find compatible waiting patients for available bed types
            best_candidate = None
            best_target_btype = None
            best_score = -1.0
            best_arrival = float("inf")
            best_pid = ""

            for btype, bcount in avail_counts.items():
                if bcount > 0:
                    cand = AllocationPolicy.select_best_patient_for_bed(
                        waiting_patients, btype, self.current_time
                    )
                    if cand:
                        wait_t = self.current_time - cand.arrival_time
                        cand_score = AllocationPolicy.calculate_priority(cand.acuity, wait_t)
                        
                        # Compare candidate across bed types using tie-breaking
                        if (cand_score > best_score) or \
                           (cand_score == best_score and cand.arrival_time < best_arrival) or \
                           (cand_score == best_score and cand.arrival_time == best_arrival and cand.patient_id < best_pid):
                            best_candidate = cand
                            best_target_btype = btype
                            best_score = cand_score
                            best_arrival = cand.arrival_time
                            best_pid = cand.patient_id

            if best_candidate and best_target_btype:
                # Perform allocation evaluation
                decision = AllocationPolicy.evaluate_allocation(
                    best_candidate, avail_counts, avail_beds_map, self.current_time
                )

                if decision.decision == "ADMITTED" and decision.bed_id:
                    # Allocate bed
                    exp_release = self.current_time + best_candidate.realized_los
                    self.bed_manager.allocate_bed(
                        decision.bed_id, best_candidate.patient_id, self.current_time, exp_release
                    )

                    # Update patient state
                    best_candidate.status = "ADMITTED"
                    best_candidate.assigned_bed_id = decision.bed_id
                    best_candidate.admission_time = self.current_time
                    best_candidate.waiting_time = self.current_time - best_candidate.arrival_time
                    self.queue_manager.remove_from_waiting(best_candidate.patient_id)

                    # Schedule discharge event
                    discharge_event = Event(
                        timestamp=exp_release,
                        event_type=EventType.PATIENT_DISCHARGE,
                        patient_id=best_candidate.patient_id,
                        data={"bed_id": decision.bed_id}
                    )
                    heapq.heappush(self.event_queue, discharge_event)

                    self._record_decision(decision, self.current_time)
                    allocated_any = True

            if not allocated_any:
                break

    def run(self) -> Dict[str, Any]:
        """
        Executes complete simulation.
        """
        start_wall_time = time.time()

        self.bed_manager.reset()
        self.queue_manager.reset()
        self.event_queue.clear()
        self.decisions.clear()
        self.avoidable_specialized_count = 0
        self.occupancy_over_time.clear()
        self.waiting_over_time.clear()

        # Step 1: Pre-generate synthetic arrivals
        patient_cohort = self._generate_synthetic_patients()

        # Schedule arrival events
        for p in patient_cohort:
            self.queue_manager.add_patient(p)
            arrival_event = Event(
                timestamp=p.arrival_time,
                event_type=EventType.PATIENT_ARRIVAL,
                patient_id=p.patient_id
            )
            heapq.heappush(self.event_queue, arrival_event)

        # Step 2: Main Event Loop
        step_counter = 0
        while self.event_queue:
            event = heapq.heappop(self.event_queue)
            self.current_time = event.timestamp

            # Check 240-min rejections for waiting queue
            self._check_and_reject_expired_waiting()

            if event.event_type == EventType.PATIENT_ARRIVAL:
                patient = self.queue_manager.get_patient(event.patient_id)
                if patient and patient.status == "WAITING":
                    # Attempt allocation
                    avail_counts = self.bed_manager.get_available_counts()
                    avail_beds_map = {
                        "general": self.bed_manager.get_available_beds_by_type("general"),
                        "monitored": self.bed_manager.get_available_beds_by_type("monitored"),
                        "critical": self.bed_manager.get_available_beds_by_type("critical")
                    }

                    decision = AllocationPolicy.evaluate_allocation(
                        patient, avail_counts, avail_beds_map, self.current_time
                    )

                    if decision.decision == "ADMITTED" and decision.bed_id:
                        exp_release = self.current_time + patient.realized_los
                        self.bed_manager.allocate_bed(
                            decision.bed_id, patient.patient_id, self.current_time, exp_release
                        )
                        patient.status = "ADMITTED"
                        patient.assigned_bed_id = decision.bed_id
                        patient.admission_time = self.current_time
                        patient.waiting_time = self.current_time - patient.arrival_time
                        self.queue_manager.remove_from_waiting(patient.patient_id)

                        discharge_event = Event(
                            timestamp=exp_release,
                            event_type=EventType.PATIENT_DISCHARGE,
                            patient_id=patient.patient_id,
                            data={"bed_id": decision.bed_id}
                        )
                        heapq.heappush(self.event_queue, discharge_event)
                        self._record_decision(decision, self.current_time)
                    else:
                        self._record_decision(decision, self.current_time)

            elif event.event_type == EventType.PATIENT_DISCHARGE:
                patient = self.queue_manager.get_patient(event.patient_id)
                bed_id = event.data.get("bed_id")
                if bed_id:
                    self.bed_manager.release_bed(bed_id)
                if patient:
                    patient.status = "DISCHARGED"
                    patient.discharge_time = self.current_time

                # Discharge freed capacity -> re-evaluate waiting queue
                self._attempt_allocations()

            # Record telemetry sample periodically
            step_counter += 1
            if step_counter % 20 == 0:
                occ = self.bed_manager.get_occupied_counts()
                waiting_len = len(self.queue_manager.get_waiting_patients(self.current_time))
                self.occupancy_over_time.append({
                    "time": round(self.current_time, 1),
                    "general": occ["general"],
                    "monitored": occ["monitored"],
                    "critical": occ["critical"],
                    "total": sum(occ.values())
                })
                self.waiting_over_time.append({
                    "time": round(self.current_time, 1),
                    "count": waiting_len
                })

        # Process any remaining waiting patients at simulation end
        for p in self.queue_manager.get_all_patients():
            if p.status == "WAITING":
                final_wait = self.current_time - p.arrival_time
                p.waiting_time = final_wait
                if final_wait >= 240.0:
                    p.status = "REJECTED"

        elapsed_seconds = time.time() - start_wall_time

        # Calculate final competition metrics
        all_p = self.queue_manager.get_all_patients()
        metrics = CompetitionMetrics.calculate_metrics(
            all_p,
            self.avoidable_specialized_count,
            elapsed_seconds,
            total_cohort_size=self.total_patients
        )

        n_admitted = sum(1 for p in all_p if p.status in ["ADMITTED", "DISCHARGED"])
        n_rejected = sum(1 for p in all_p if p.status == "REJECTED")
        avg_wait = float(np.mean([p.waiting_time for p in all_p])) if all_p else 0.0

        return {
            "run_id": self.run_id,
            "seed": self.seed,
            "total_arrivals": len(all_p),
            "admitted": n_admitted,
            "rejected": n_rejected,
            "average_wait": round(avg_wait, 2),
            "weighted_wait_utility": metrics["weighted_wait_utility"],
            "critical_wait_utility": metrics["critical_wait_utility"],
            "rejection_utility": metrics["rejection_utility"],
            "specialized_capacity_utility": metrics["specialized_capacity_utility"],
            "overall_score": metrics["overall_score"],
            "runtime_seconds": metrics["runtime_seconds"],
            "patients": all_p,
            "decisions": self.decisions,
            "occupancy_over_time": self.occupancy_over_time,
            "waiting_over_time": self.waiting_over_time
        }
