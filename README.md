# simple-cmms

Minimal CMMS skeleton for small manufacturers.

Folders:
- `backend`: FastAPI app
- `frontend`: Next.js (App Router) UI

See `.env.example` for required environment variables.

Quick run (backend):

1. Create virtualenv and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

2. Create DB and export `DATABASE_URL` then run:

```bash
uvicorn backend.app.main:app --reload --port 8080
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Deployment: see `cloudbuild.yaml` for a simple Cloud Build + Cloud Run template.
# smamainte
中小製造業向けcmms
