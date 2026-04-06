# RNK Civil — Python web app (Streamlit + MongoDB)

Browser app with **company onboarding**, **users**, **employees**, **clients**, **role-based access**, and civil operations modules (projects, workers, attendance, expenses, payroll, invoices).

## Requirements

- Python **3.10+** recommended  
- **MongoDB** (MongoDB Atlas or self-hosted)  
- Dependencies: see `requirements.txt`

## One `.env` file (single source of truth)

Use **one** file only: **`<repository-root>/.env`** (same folder as `README.md` / `.env.example`).

Put **Mongo** variables there for this Streamlit app **and** you can keep your **Node API** variables (`PORT`, `JWT_*`, `CORS`, etc.) in that **same** file. The Python app reads only the Mongo-related keys; it ignores the rest.

Do **not** maintain a second `.env` inside `python_app/` — everything loads from the repo root.

## Environment variables (Mongo)

**You do not need any extra env vars** for Streamlit beyond a working Mongo connection. If your `.env` already has `MONGODB_USERNAME`, `MONGODB_PASSWORD`, `MONGODB_CLUSTER`, `MONGODB_DATABASE`, and optionally `MONGODB_APP_NAME` / `MONGODB_AUTH_SOURCE`, that is enough — no separate “app secrets” or JWT variables are required for this Python UI.

Create or edit **`.env`** in the **repository root** (see `.env.example`):

| Variable | Required | Description |
|----------|----------|-------------|
| `MONGO_URI` / `MONGODB_URI` / `MONGODB_URL` | Yes* | Full connection string (first non-empty wins) |
| `MONGO_USER` / `MONGODB_USERNAME` | Yes* | Database user |
| `MONGO_PASSWORD` / `MONGODB_PASSWORD` | Yes* | Database password |
| `MONGO_HOST` / `MONGODB_CLUSTER` | Yes* | Host only, e.g. `cluster0.xxxxx.mongodb.net` |
| `MONGO_DB_NAME` / `MONGODB_DATABASE` | No | Database name (default `rnk_civil`) |
| `MONGO_APP_NAME` / `MONGODB_APP_NAME` | No | e.g. `Cluster0` |
| `MONGO_AUTH_SOURCE` / `MONGODB_AUTH_SOURCE` | No | e.g. `admin` |
| `MONGO_SCHEME` / `MONGODB_SCHEME` | No | Default `mongodb+srv` |

\* Either a full URI **or** split fields (`MONGO_*` **or** the `MONGODB_*` names used by your Node API).

JWT, `PORT`, `CORS`, etc. are **not** used by this Streamlit app.

Never commit `.env` or real credentials.

## Install

```bash
cd "/path/to/Powe-BI"
python3 -m venv .venv
. .venv/bin/activate
pip install -r python_app/requirements.txt
```

## Run

```bash
cd python_app
streamlit run app.py
```

Open the URL shown (usually `http://localhost:8501`).

## First-time flow

1. **Create company** — company name + admin name + email + password.  
2. **Sign in** with that email.  
3. Add **OT rules**, **projects**, **sites**, **workers**, then **attendance** / **expenses**.  
4. **Company admin** can invite more **app users** under **Team & employees** (tab “App users”).

## Roles

| Role | Typical access |
|------|----------------|
| `company_admin` | All modules + user invites + company profile |
| `manager` | Operations + payroll + invoices (no company settings) |
| `finance` | Expenses, payroll, invoices, dashboard |
| `site_ops` | Sites, workers, attendance, expenses |
| `viewer` | Read-only dashboard / projects |

Exact page mapping is in `core/roles.py`.

## Data model

All operational data is scoped by **`company_id`** in MongoDB. Collections include: `companies`, `users`, `clients`, `employees`, `ot_rules`, `projects`, `sites`, `workers`, `attendance`, `expenses`, `payroll_runs`, `payroll_lines`, `invoices`.

## Security notes

- Passwords are stored as **bcrypt** hashes.  
- **No row-level project ACL** yet — all users in a company see that company’s data; refine with `project_id` filters later if needed.  
- Run behind **HTTPS** and restrict network access in production.

## Project layout

```
python_app/
  app.py              # Entry: Mongo check, auth, RBAC router
  config.py           # Env loading
  db/mongo.py         # Client, indexes
  core/roles.py       # RBAC page map
  core/security.py    # Password hashing
  services/auth_service.py
  services/civil_store.py
  ui/theme.py
  ui/pages_main.py    # Module screens
```

## Excel / Power Platform

The **Excel** workbook and **Power Platform** docs in this repo are separate tracks; this app is **Mongo + Streamlit** only.
