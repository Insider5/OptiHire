# OptiHire — Deployment Guide

## Local Development

### Prerequisites
- Python 3.10+
- pip

### Setup

```bash
# Clone the repo and enter the project folder
cd tax

# Create a virtual environment
python -m venv .venv
.venv\Scripts\activate       # Windows
# source .venv/bin/activate  # Linux / macOS

# Install dependencies
pip install -r requirements.txt

# Download the spaCy language model
python -m spacy download en_core_web_sm

# Copy the env template and fill in your credentials
cp .env.example .env
# Edit .env: set SECRET_KEY, GEMINI_API_KEY, and optional MAIL_* settings
```

### Run in Development

```bash
python run.py
# App available at http://127.0.0.1:5000
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | ✅ | Flask session secret (generate a random string) |
| `FLASK_ENV` | ✅ | `development` or `production` |
| `GEMINI_API_KEY` | ✅ | Google Gemini API key (for AI questions) |
| `MAIL_SERVER` | ❌ | SMTP server (e.g., `smtp.gmail.com`) |
| `MAIL_PORT` | ❌ | SMTP port (default `587`) |
| `MAIL_USE_TLS` | ❌ | `True` / `False` |
| `MAIL_USERNAME` | ❌ | SMTP login username |
| `MAIL_PASSWORD` | ❌ | SMTP login password |
| `MAIL_DEFAULT_SENDER` | ❌ | From address, e.g. `OptiHire <no-reply@optihire.ai>` |

> Email is **optional**. If `MAIL_USERNAME` is not set, status-change emails are silently skipped.

---

## Production Deployment (Render / Railway / Heroku)

### Step 1 — Add a `Procfile`
Already included:
```
web: gunicorn run:app
```

### Step 2 — Install gunicorn
```bash
pip install gunicorn
pip freeze > requirements.txt
```

### Step 3 — Set environment variables on the platform
Set all variables from the table above in the platform's dashboard or config.

### Step 4 — Persistent storage
The current storage backend writes JSON files to `data/`. In a cloud environment these files are **ephemeral** (wiped on restart). For production, migrate to:
- **SQLite** (simplest) — store the DB file on a mounted volume
- **PostgreSQL** (recommended) — use Flask-SQLAlchemy + Alembic

### Step 5 — Deploy
```bash
git push heroku main
# or connect your repo on Render/Railway and push
```

---

## Rate Limiting

The login endpoint is rate-limited to **10 POST requests per minute** per IP to prevent brute-force attacks. This uses Flask-Limiter with in-memory storage (development). For production, set a Redis backend:

```python
# config.py
RATELIMIT_STORAGE_URL = "redis://localhost:6379/0"
```

---

## Security Checklist

- [x] CSRF protection on all POST forms (Flask-WTF)
- [x] Passwords hashed with Bcrypt
- [x] Rate limiting on login (10 req/min)
- [x] Secret key from environment variable
- [x] Error pages (403 / 404 / 500)
- [ ] HTTPS enforced (configure on reverse proxy / platform)
- [ ] Persistent storage (migrate from JSON to DB for production)
- [ ] Email credentials stored in environment, never in code

---

## Accessing the App

| Route | Description |
|---|---|
| `/` | Landing page |
| `/auth/register` | Register as candidate or recruiter |
| `/auth/login` | Login |
| `/jobs/` | Browse job listings |
| `/candidates/upload-resume` | Upload & parse resume |
| `/dashboard/candidate` | Candidate dashboard |
| `/dashboard/recruiter` | Recruiter dashboard |
| `/analytics/candidate` | Candidate analytics |
| `/analytics/recruiter` | Recruiter analytics |
