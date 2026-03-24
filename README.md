# SOC Threat Monitoring & Alert Investigation Platform

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green)
![React](https://img.shields.io/badge/React-18-blue)
![Tests](https://img.shields.io/badge/tests-pytest-6F42C1)
![MITRE ATT&CK](https://img.shields.io/badge/MITRE%20ATT%26CK-15%20rules-red)

An analyst-style, **fully local** SOC simulation: ingest JSON security events, evaluate **15 YAML detection rules** mapped to **MITRE ATT&CK**, triage alerts in a **React dashboard**, manage **cases**, view **metrics** (MTTD, FP rate, volume), and open **investigation playbooks**.

**Target repository:** [github.com/Rutujadb/soc-threat-monitoring-platform](https://github.com/Rutujadb/soc-threat-monitoring-platform)

---

## Features

- **Log ingestion** — `POST /api/ingest` with Windows auth, DNS, Sysmon, NetFlow, and Linux auth shapes (normalized to one schema).
- **Detection engine** — Threshold, pattern (regex), after-hours, sequence, and baseline hooks; rules hot-reloaded from `rules/` on each evaluation.
- **SQLite + SQLAlchemy** — Events, alerts, cases, notes; no cloud dependencies.
- **REST API** — FastAPI with OpenAPI at `http://localhost:8000/docs`.
- **React UI** — Alert queue & detail, ATT&CK heatmap, metrics (Recharts), cases board, rules catalog, playbook viewer (Markdown).
- **Simulator** — `simulate_logs.py` generates noise + attack bursts against the API.
- **Tests** — `pytest` for normalizer, detection engine, and API (`TESTING=1` + in-memory SQLite).
- **Docker Compose** — One command to run API + Vite dev server.

---

## Architecture

```
                    ┌─────────────────┐
                    │  simulate_logs  │
                    │  (Python/Faker) │
                    └────────┬────────┘
                             │ POST /api/ingest
                             ▼
                    ┌─────────────────┐      ┌──────────────┐
                    │   Normalizer     │─────▶│   SQLite     │
                    │  (5 log types)   │      │ events/alerts│
                    └────────┬────────┘      │    /cases    │
                             │               └───────┬──────┘
                             ▼                       │
                    ┌─────────────────┐               │
                    │ DetectionEngine │               │
                    │ rules/*.yaml    │               │
                    └────────┬────────┘               │
                             │ alerts                  │
                             ▼                       │
                    ┌─────────────────┐◀──────────────┘
                    │   FastAPI :8000  │
                    └────────┬────────┘
                             │ JSON
                             ▼
                    ┌─────────────────┐
                    │ React + Vite    │
                    │ Dashboard :3000 │
                    └─────────────────┘
```

---

## Quick start (Docker Compose)

**Prerequisites:** Docker Desktop (or Docker Engine + Compose v2).

1. Clone the repository (or use this folder as the repo root).
2. From the **repository root** (where `docker-compose.yml` lives):

```bash
docker compose up --build
```

3. Wait for installs to finish, then open:
   - **UI:** http://localhost:3000  
   - **API docs:** http://localhost:8000/docs  
   - **Health:** http://localhost:8000/health  

The API stores its database in the `soc_data` Docker volume (`DATABASE_URL=sqlite:////app/data/soc_platform.db` inside the container). Rules and playbooks are mounted read-only from `./rules` and `./playbooks`.

---

## Local setup (without Docker) — step by step

### 1. Prerequisites

- **Python** 3.10+ (3.11+ recommended) and **pip**
- **Node.js** 18+ and **npm**
- Git (optional, for version control)

### 2. Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

From the `backend` directory, start the API (repo root must contain `rules/` and `playbooks/` next to `backend/`):

```powershell
cd "d:\path\to\soc-threat-monitoring-platform\backend"
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

On first startup, SQLite creates `backend\soc_platform.db` (unless you set `DATABASE_URL`).

### 3. Frontend

In a **second** terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:3000 — Vite proxies `/api` to `http://127.0.0.1:8000`.

### 4. Generate traffic (simulator)

With the API running, from `backend` with venv active:

```powershell
cd backend
python -m ingestor.simulate_logs --rate 3 --attack-ratio 0.25
```

Options:

| Flag | Meaning |
|------|---------|
| `--base-url` | API root (default `http://127.0.0.1:8000`) |
| `--rate` | Approximate events per second |
| `--attack-ratio` | Probability of injecting an attack scenario (0.0–1.0) |
| `--duration` | Seconds to run (`0` = until Ctrl+C) |

Refresh the **Alerts** page to see new detections.

### 5. Tests

```powershell
cd backend
$env:TESTING="1"
pytest
```

CI runs the same via `.github/workflows/tests.yml`.

---

## Project layout

| Path | Purpose |
|------|---------|
| `backend/api/` | FastAPI app, routes, DB models |
| `backend/ingestor/` | Normalizer, Pydantic schemas, `simulate_logs.py` |
| `backend/detection/` | Rule loader, engine, alerts, baselines |
| `rules/` | YAML detection rules (`RULE-001` … `RULE-015`) |
| `playbooks/` | Markdown IR playbooks |
| `frontend/` | React (Vite + Tailwind + Recharts) |

---

## Detection rules catalog

| ID | Name | Example MITRE |
|----|------|---------------|
| RULE-001 | Brute Force Authentication | T1110 |
| RULE-002 | Password Spray | T1110.003 |
| RULE-003 | DNS Tunneling (High Frequency) | T1071.004 |
| RULE-004 | DNS Tunneling (Long Subdomain) | T1071.004 |
| RULE-005 | Privilege Escalation via Sudo | T1548.003 |
| RULE-006 | Pass-the-Hash Indicator | T1550.002 |
| RULE-007 | Kerberoasting (SPN Ticket Spike) | T1558.003 |
| RULE-008 | Lateral Movement via PsExec | T1021.002 |
| RULE-009 | LSASS Access Attempt | T1003.001 |
| RULE-010 | New Local Admin Activity | T1136.001 |
| RULE-011 | Logon Outside Business Hours | T1078 |
| RULE-012 | Internal Port Scan | T1046 |
| RULE-013 | Suspicious PowerShell Execution | T1059.001 |
| RULE-014 | Scheduled Task Creation | T1053.005 |
| RULE-015 | Service Installed on Endpoint | T1543.003 |

Official technique pages: https://attack.mitre.org/

---

## API overview

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/ingest` | Ingest one event (`source_type` + `log`) |
| GET | `/api/alerts` | List/filter alerts |
| GET | `/api/alerts/{id}` | Alert detail + notes + raw event |
| PATCH | `/api/alerts/{id}` | Update status, assignee, add note |
| GET/POST | `/api/cases` | List / create cases |
| PATCH | `/api/cases/{id}` | Update case |
| POST | `/api/cases/{id}/alerts` | Link alert to case |
| GET | `/api/cases/{id}/detail` | Case + linked alerts |
| GET | `/api/metrics` | Dashboard metrics |
| GET | `/api/rules` | Rules + trigger counts |
| GET | `/api/attack-heatmap` | Technique → count |
| GET | `/api/playbooks/{rule_id}` | Raw Markdown playbook |

---

## Screenshots

_Add screenshots of the Alert Queue, Alert Detail, ATT&CK Matrix, and Metrics pages here after you run the UI._

---

## Contributing

1. Fork / branch from `main`.
2. Run `pytest` with `TESTING=1` before pushing.
3. Keep rules and playbooks in sync when adding detections.

---

## License

Use and modify for portfolio, learning, and interviews. Add a license file if you publish formally.

---

## Resume bullet (suggested)

Built a full-stack **SOC Threat Monitoring Platform** (Python/FastAPI/React) with simulated alert ingestion, **15 MITRE ATT&CK–mapped** YAML rules, analyst triage and case workflows, detection metrics (**MTTD**, **false-positive rate**), Markdown **playbooks**, and **pytest** + **GitHub Actions** CI.
