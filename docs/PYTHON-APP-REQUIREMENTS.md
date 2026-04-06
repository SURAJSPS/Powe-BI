# Python app — deployment requirements

## Runtime

| Item | Version / note |
|------|----------------|
| Python | 3.10+ (3.11 recommended) |
| OS | macOS, Linux, or Windows |
| RAM | 512 MB+ for Streamlit |

## Services

| Service | Required | Note |
|---------|----------|------|
| **MongoDB** | Yes | Atlas (recommended) or self-hosted; replica set optional |
| Connection | `MONGO_URI` | See repository `.env.example` |

## Python packages

Install from `python_app/requirements.txt`:

- `streamlit` — UI  
- `pymongo` — MongoDB driver  
- `python-dotenv` — load `.env`  
- `bcrypt` — password hashing  
- `pandas` — tables / payroll estimate  
- `sqlalchemy` — optional; legacy SQLite files only  

## Environment variables

| Variable | Required | Example |
|----------|----------|---------|
| `MONGO_URI` | Yes | `mongodb+srv://user:pass@cluster.mongodb.net/` |
| `MONGO_DB_NAME` | No | `rnk_civil` |

## Network

- App binds to localhost by default (`streamlit run`).  
- For team access, use HTTPS reverse proxy (nginx, Caddy) or Streamlit Community Cloud with secrets — **do not** expose Mongo credentials in the frontend.

## Optional next steps

- Email verification for registration  
- Password reset  
- Per-project permissions  
- API layer (FastAPI) + mobile clients  
