from typing import List, Dict, Any

class CompetitionMetrics:
    @staticmethod
    def calculate_metrics(
        patients: List[Any],
        avoidable_specialized_count: int,
        runtime_seconds: float,
        total_cohort_size: int = 500
    ) -> Dict[str, float]:
        """
        Calculates exact hackathon competition utilities and overall score.
        """
        if not patients:
            return {
                "weighted_wait_utility": 1.0,
                "critical_wait_utility": 1.0,
                "rejection_utility": 1.0,
                "specialized_capacity_utility": 1.0,
                "overall_score": 100.0,
                "runtime_seconds": runtime_seconds
            }

        total_weighted_wait = 0.0
        total_weight = 0.0

        crit_wait_sum = 0.0
        n_critical = 0

        n_rejected = 0
        n_admitted = 0

        for p in patients:
            weight = getattr(p, 'acuity_weight', 1)
            wait = getattr(p, 'waiting_time', 0.0)
            status = getattr(p, 'status', 'WAITING')
            acuity = getattr(p, 'acuity', 1)

            capped_wait = min(max(0.0, wait), 240.0)
            total_weighted_wait += weight * capped_wait
            total_weight += weight

            if acuity == 3:
                n_critical += 1
                crit_wait_sum += capped_wait

            if status == "REJECTED":
                n_rejected += 1
            elif status in ["ADMITTED", "DISCHARGED"]:
                n_admitted += 1

        # 1. Weighted wait utility
        if total_weight > 0:
            u_wait = max(0.0, min(1.0, 1.0 - (total_weighted_wait / (240.0 * total_weight))))
        else:
            u_wait = 1.0

        # 2. Critical wait utility
        if n_critical > 0:
            u_critical = max(0.0, min(1.0, 1.0 - (crit_wait_sum / (240.0 * n_critical))))
        else:
            u_critical = 1.0

        # 3. Rejection utility
        u_reject = max(0.0, min(1.0, 1.0 - (n_rejected / float(total_cohort_size))))

        # 4. Specialized capacity utility
        if n_admitted > 0:
            u_specialized = max(0.0, min(1.0, 1.0 - (avoidable_specialized_count / float(n_admitted))))
        else:
            u_specialized = 1.0

        # 5. Runtime / Reproducibility score (5 points max)
        # Measured runtime: <= 5.0s gives 1.0 score (5 points), smoothly degrading if longer
        if runtime_seconds <= 5.0:
            runtime_score = 1.0
        else:
            runtime_score = max(0.0, min(1.0, 1.0 - (runtime_seconds - 5.0) / 20.0))

        # Competition overall score (100 pts max)
        overall_score = (
            (u_wait * 45.0) +
            (u_critical * 20.0) +
            (u_reject * 15.0) +
            (u_specialized * 15.0) +
            (runtime_score * 5.0)
        )

        return {
            "weighted_wait_utility": round(u_wait, 4),
            "critical_wait_utility": round(u_critical, 4),
            "rejection_utility": round(u_reject, 4),
            "specialized_capacity_utility": round(u_specialized, 4),
            "overall_score": round(overall_score, 2),
            "runtime_seconds": round(runtime_seconds, 4)
        }
