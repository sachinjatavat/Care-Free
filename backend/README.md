# CareFlow — Smart Hospital Bed Allocation System (Backend)

> **Created by Sachin Jatavat, Krishna Khandelwal, Priyanshi Jaiswal**

CareFlow is an event-driven clinical command center backend for hospital bed allocation under severe capacity constraints.

---

## 🚀 Quick Start

### 1. Installation

```bash
cd backend
python -m pip install -r requirements.txt
```

### 2. Run Tests

```bash
pytest backend/tests/
```

### 3. Start FastAPI Server

```bash
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

- API Interactive Swagger Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- API Health Check: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

### 4. Start Frontend

Open `index.html` at the project root using any web server or static server:

```bash
python -m http.server 3000
```

Then navigate to `http://localhost:3000`.

---

## 🎯 Architecture & Allocation Policy

### Simulation Architecture
- **Discrete-Event Simulator**: Queue-based event processing (`PATIENT_ARRIVAL` and `PATIENT_DISCHARGE`) using NumPy PCG64 PRNG generator (`np.random.Generator(np.random.PCG64(seed))`).
- **Reproducibility**: Development seed `20260911` generates identical stochastic arrival streams, acuity assignments, and lognormal stay durations every run.
- **500 Synthetic Arrivals**: Inter-arrivals $\sim \text{Exponential}(\text{mean}=2.5\text{m})$, Acuity probabilities: Level 1 (60%), Level 2 (30%), Level 3 (10%).

### Bed Capacities & Compatibility
- **General Care (30 beds)**: `G-01` through `G-30` (Acuity L1, L2 overflow, L3 overflow)
- **Monitored Telemetry (10 beds)**: `M-01` through `M-10` (Acuity L1, L2, L3 overflow)
- **Critical Care ICU (5 beds)**: `C-01` through `C-05` (Strict L3 priority, L1/L2 emergency fallback)

### Online Allocation Policy (`backend/core/allocation_policy.py`)
- Receives ONLY state revealed up to current simulation time $t$ (future arrivals & realized stay durations are strictly hidden).
- **Priority Calculation**: $\text{Priority Score} = w_i \times \min(t_{\text{wait}}, 240)$, where $w_1=1, w_2=3, w_3=8$.
- **Specialized Bed Preservation**:
  - Level 1: Prefers General $\rightarrow$ Monitored $\rightarrow$ Critical
  - Level 2: Prefers Monitored $\rightarrow$ Critical
  - Level 3: Critical only
- **240-Minute Rejection Rule**: Patients waiting longer than 240 minutes are automatically marked `REJECTED` and removed from the queue.
- **Non-Eviction Invariant**: Once admitted, a patient is never forcibly evicted or downgraded.

---

## 📊 Competition Metrics Formulas

1. **Weighted Wait Utility**:
   $$U_{\text{wait}} = \text{clip}\left(1 - \frac{\sum w_i \min(\text{wait}_i, 240)}{240 \sum w_i}, 0, 1\right)$$

2. **Critical Wait Utility**:
   $$U_{\text{critical}} = \text{clip}\left(1 - \frac{\sum_{\text{acuity}=3} \min(\text{wait}_i, 240)}{240 \times N_{\text{critical}}}, 0, 1\right)$$

3. **Rejection Utility**:
   $$U_{\text{reject}} = \text{clip}\left(1 - \frac{N_{\text{rejected}}}{500}, 0, 1\right)$$

4. **Specialized Capacity Utility**:
   $$U_{\text{specialized}} = \text{clip}\left(1 - \frac{N_{\text{avoidable\_specialized}}}{N_{\text{admitted}}}, 0, 1\right)$$

5. **Overall Score**:
   $$\text{Overall Score} = 45 U_{\text{wait}} + 20 U_{\text{critical}} + 15 U_{\text{reject}} + 15 U_{\text{specialized}} + 5 U_{\text{runtime}}$$

---

## 🔌 API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | System health check and seed status |
| `GET` | `/api/dashboard` | KPI metrics, bed capacity summary, and recent decisions |
| `GET` | `/api/patients/waiting` | Live priority-sorted waiting queue |
| `GET` | `/api/patients/{id}` | Patient history and status |
| `POST` | `/api/patients/simulate-arrival` | Authoritative synthetic arrival trigger |
| `GET` | `/api/beds` | Real-time status for all 45 beds |
| `GET` | `/api/beds/{id}` | Bed occupancy detail |
| `POST` | `/api/allocation/decision` | Execute allocation decision for patient |
| `GET` | `/api/decisions` | Complete audit decision logs |
| `GET` | `/api/decisions/{patient_id}` | Decision history for specific patient |
| `GET` | `/api/export/decisions` | Download decision audit log as CSV |
| `POST` | `/api/simulation/run` | Execute 500-patient Monte Carlo run (Seed: 20260911) |
| `GET` | `/api/simulation/status` | Current simulator progress |
| `GET` | `/api/simulation/results` | Latest simulation metrics & results |
| `GET` | `/api/analytics` | Telemetry series and competition scoring breakdown |
| `GET` | `/api/analytics/policy-comparison` | Policy benchmarking (CareFlow vs FIFO vs Greedy) |
| `GET` | `/api/analytics/explain/{patient_id}` | Natural language explanation of allocation decision |
| `GET` | `/api/hospitals` | Regional hospital network directory & pricing tiers |
| `GET` | `/api/hospitals/{hospital_id}` | Detailed hospital profile & bed availability |
| `POST` | `/api/ambulance/dispatch` | Emergency ambulance dispatch & bed reservation |
| `POST` | `/api/chat` | AI Clinical Triage & Capacity Support Chatbot |
