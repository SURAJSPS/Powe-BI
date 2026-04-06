# RNK Civil — Python web app (Streamlit + MongoDB)

Browser app with **company onboarding**, **users**, **employees**, **clients**, **role-based access**, and civil operations modules (projects, workers, attendance, expenses, payroll, invoices).

## Requirements

- Python **3.10+** recommended  
- **MongoDB** (MongoDB Atlas or self-hosted)  
- Dependencies: see `requirements.txt`

## Environment variables

Create a **`.env`** file in the **repository root** (same folder as `.env.example`):

| Variable | Required | Description |
|----------|----------|-------------|
| `MONGO_URI` | **Yes** | Connection string (e.g. Atlas `mongodb+srv://...`) |
| `MONGO_DB_NAME` | No | Database name (default: `rnk_civil`) |

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
