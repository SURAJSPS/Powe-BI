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
| Connection | `MONGODB_*` or `MONGO_URI` | See repository root `.env` (not committed) |

## Python packages

Install from `python_app/requirements.txt`:

- `streamlit` — UI  
- `pymongo` — MongoDB driver  
- `python-dotenv` — load `.env`  
- `bcrypt` — password hashing  
- `pandas` — tables / payroll estimate  
- `sqlalchemy` — optional; legacy SQLite files only  

## Environment variables

Configure **`Powe-BI/.env`** (single file; no `.env.example` in repo).

| Variable | Required | Example |
|----------|----------|---------|
| `MONGODB_USERNAME` | Yes* | Atlas database user |
| `MONGODB_PASSWORD` | Yes* | Must match **Database Access** |
| `MONGODB_CLUSTER` | Yes* | Host only, e.g. `cluster0.xxxxx.mongodb.net` |
| `MONGODB_DATABASE` | No | e.g. `tepo` (default `rnk_civil` if unset) |
| `MONGODB_APP_NAME` | No | e.g. `Cluster0` |
| `MONGODB_AUTH_SOURCE` | No | e.g. `admin` |
| `MONGODB_URI` / `MONGO_URI` | alt | Full URI instead of split fields |

\* Or one full URI instead of username/password/cluster.

**Authentication failed:** reset password in Atlas → **Database Access**, update `MONGODB_PASSWORD`, save `.env`, restart Streamlit. Passwords with special characters are URL-encoded when using split variables.

**Cannot reach cluster:** **Atlas → Network Access** → allow your IP (or `0.0.0.0/0` for testing).

## Network

- App binds to localhost by default (`streamlit run`).  
- For team access, use HTTPS reverse proxy (nginx, Caddy) or Streamlit Community Cloud with secrets — **do not** expose Mongo credentials in the frontend.

## Optional next steps

- Email verification for registration  
- Password reset  
- Per-project permissions  
- API layer (FastAPI) + mobile clients  
