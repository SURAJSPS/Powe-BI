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
| Connection | `MONGO_URI` or split vars | See repository root `.env` |

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
| `MONGO_URI` | Use this **or** split vars | Full string from Atlas **Connect → Drivers** |
| `MONGO_USER` | If no URI | Database username (Atlas **Database Access**) |
| `MONGO_PASSWORD` | If no URI | Must match that user’s password in Atlas |
| `MONGO_HOST` | If no URI | Host only, e.g. `cluster0.xxxxx.mongodb.net` |
| `MONGO_SCHEME` | No | Default `mongodb+srv` |
| `MONGO_DB_NAME` | No | `rnk_civil` |

**Authentication failed:** reset the user password in **Atlas → Database Access**, update `MONGO_PASSWORD` (or full `MONGO_URI`), save `.env`, restart Streamlit. With split variables, special characters in the password are URL-encoded automatically.

**Cannot reach cluster:** **Atlas → Network Access** → allow your IP (or `0.0.0.0/0` for testing).

## Network

- App binds to localhost by default (`streamlit run`).  
- For team access, use HTTPS reverse proxy (nginx, Caddy) or Streamlit Community Cloud with secrets — **do not** expose Mongo credentials in the frontend.

## Optional next steps

- Email verification for registration  
- Password reset  
- Per-project permissions  
- API layer (FastAPI) + mobile clients  
