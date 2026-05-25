---
name: run-cardora
description: Run, start, build, screenshot, verify, test, or smoke-test the Cardora app. Launches both the Next.js frontend (port 3000) and the FastAPI backend (port 8000). Use this to confirm changes work end-to-end.
---

# run-cardora

Cardora is a full-stack credit card statement analyzer. The **backend** is a FastAPI (Python) server at `http://localhost:8000`; the **frontend** is Next.js at `http://localhost:3000`. The AI pipeline (Gemini + PyPDF2) runs inside the backend.

Paths below are relative to the repo root (`E:\Cardora\` on Windows, wherever it's cloned).

---

## Prerequisites

**Python venv** must have these packages installed. Run once after cloning:

```powershell
venv\Scripts\pip install google-generativeai PyPDF2
```

> **Gotcha:** `google-generativeai` and `PyPDF2` are used by `app/core/gemini_service.py` but are **not listed in `requirements.txt`**. The system Python may have them, but the venv won't unless you run the above. The backend starts and serves non-AI endpoints fine without `google-generativeai`, but PDF upload will fail.

**Node.js** (any modern version) for the frontend — `node_modules` is already populated.

**PostgreSQL** must be running on port **5433** (not the default 5432). The `.env` file has the connection string.

**`.env` file** at repo root is required and contains real credentials (not committed). It must exist with:
```
DATABASE_URL=postgresql://postgres:<password>@localhost:5433/cardora_dev
GEMINI_API_KEY=<real key>
SECRET_KEY=<any non-empty string>
```

---

## Build

No explicit build step for development. Frontend deps are pre-installed.

```powershell
# Install frontend deps (only needed after fresh clone or package.json changes)
npm --prefix frontend install

# Run DB migrations (only needed after schema changes or fresh DB)
venv\Scripts\python.exe -m alembic upgrade head

# Seed default categories (run once on a fresh DB)
venv\Scripts\python.exe app\core\seed_data.py
```

---

## Run (agent path — primary)

### Step 1: Launch both servers

The `launch.json` at `.claude/launch.json` defines both servers. Use `preview_start` for each:

- Name `"frontend"` → `npm --prefix frontend run dev` → port 3000
- Name `"backend"` → `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload` → port 8000

If `preview_start` is unavailable, start them in PowerShell background jobs:

```powershell
# Backend
Start-Job -ScriptBlock { Set-Location "E:\Cardora"; venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload }

# Frontend
Start-Job -ScriptBlock { Set-Location "E:\Cardora"; npm --prefix frontend run dev }
```

### Step 2: Verify with the smoke script

```powershell
.\.claude\skills\run-cardora\smoke.ps1
```

The script checks all critical API endpoints and prints PASS/FAIL for each. All should be PASS when the app is healthy.

### Step 3: Screenshot the UI (for visual changes)

Use `preview_screenshot` with the frontend server ID to capture the current view, then navigate to specific pages:

| Page | URL path |
|---|---|
| Landing | `/` |
| Dashboard | `/dashboard` |
| Upload Statement | `/upload` |
| Transactions | `/transactions` |
| Analytics | `/analytics` |
| Insights | `/insights` |
| Cards | `/cards` |
| Settings | `/settings` |

Use `preview_snapshot` to get the accessibility tree (element text, roles, UIDs) for asserting page content without screenshot.

---

## Run (human path)

Open two terminals at repo root:

```powershell
# Terminal 1 — backend
venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2 — frontend
npm --prefix frontend run dev
```

Open `http://localhost:3000` in a browser. Login or register. The demo account created by the seed script is `test@example.com` / (see the seed script for the default password).

Swagger docs at `http://localhost:8000/docs` for direct API exploration.

---

## Test

Backend unit/integration tests (require the DB to be up):

```powershell
venv\Scripts\python.exe -m pytest tests/ -v
```

Individual test files:

```powershell
venv\Scripts\python.exe -m pytest tests/test_api.py -v
venv\Scripts\python.exe -m pytest tests/test_login_endpoint.py -v
```

---

## Gotchas

- **`google-generativeai` missing from `requirements.txt`** — it must be pip-installed separately into the venv. Without it, the app boots fine but `/statements/upload` will raise `ModuleNotFoundError` at runtime. See Prerequisites above.

- **PostgreSQL on port 5433** — the local dev DB runs on 5433, not the default 5432. If you're setting up a fresh PostgreSQL instance, create it on 5433 or edit `DATABASE_URL` in `.env`.

- **Frontend `.env.local` must exist** at `frontend/.env.local` with `NEXT_PUBLIC_API_URL=http://localhost:8000`. Without it, all API calls 404 silently in the browser. This file is gitignored; create it from `.env.example`.

- **CORS is hardcoded for `localhost:3000/3001`** in `app/main.py`. If Next.js binds to a different port (can happen if 3000 is taken), API calls will fail with CORS errors. The browser dev console will show the error.

- **JWT token stored in `localStorage`** — the auth context in `frontend/src/shared/contexts/` reads from localStorage. On a fresh browser session with no token, all dashboard pages redirect to `/login`.

- **Gemini model name** in `gemini_service.py` uses `'gemini-pro-latest'` — if Google deprecates this alias, update it to the current model name (check `google.generativeai.list_models()`).

- **`uploads/` directory** is created on first startup, not committed to git. Uploaded PDFs land here. On a fresh clone, the directory doesn't exist until the first request.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'google.generativeai'` | `venv\Scripts\pip install google-generativeai` |
| `ModuleNotFoundError: No module named 'PyPDF2'` | `venv\Scripts\pip install PyPDF2` |
| Backend crashes with `could not connect to server` | PostgreSQL not running, or running on wrong port. Check `DATABASE_URL` in `.env`. |
| Frontend shows blank page / all routes 404 | Next.js build error. Check terminal for compile errors. |
| API calls from frontend return CORS errors | Frontend is on a port not in the CORS allowlist in `app/main.py`. Add the port or restart Next.js on 3000. |
| `alembic.util.exc.CommandError: Can't locate revision` | Run `alembic upgrade head` to apply pending migrations. |
| Login always fails with 401 | DB not seeded. Run `venv\Scripts\python.exe app\core\seed_data.py` first, then register a new user. |
