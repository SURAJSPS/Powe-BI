# RNK Civil — Python web app (Streamlit + SQLite)

Local **browser UI** for civil operations: master data, attendance, expenses, payroll helpers, invoices, dashboard.  
Data is stored in **`data/rnk_civil.db`** at the **repository root** (created on first run).

## Requirements

- Python **3.10+** recommended (3.9 may work).
- Dependencies: `streamlit`, `sqlalchemy`, `pandas` (see `requirements.txt`).

## Install

From the repo root (uses project `.venv` if you already have one):

```bash
cd "/Users/surajsps/RNK INFRATECH/IT/Powe-BI"
python3 -m venv .venv
. .venv/bin/activate
pip install -r python_app/requirements.txt
```

## Run

```bash
cd "/Users/surajsps/RNK INFRATECH/IT/Powe-BI/python_app"
streamlit run app.py
```

Open the URL shown in the terminal (usually `http://localhost:8501`).

## What’s included

| Area | Notes |
|------|--------|
| **OT rules, projects, sites, workers** | Forms + tables |
| **Attendance, expenses** | Add rows; lists below |
| **Payroll estimate** | Rough calculation from attendance + rates |
| **Payroll runs / lines** | Manual journal-style lines (use with CA for statutory) |
| **Invoices** | Simple header rows |
| **Dashboard** | Counts + period expense total |

First launch **seeds** demo data if the database is empty.

## Security

- **No login** — use only on trusted machines / private network, or add auth later (e.g. reverse proxy + SSO).
- Backup **`data/rnk_civil.db`** regularly.

## Files

| File | Role |
|------|------|
| `app.py` | Streamlit UI |
| `models.py` | SQLAlchemy models |
| `database.py` | SQLite path, `init_db`, seed |
