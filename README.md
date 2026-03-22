# ScholarForm AI — Automated Academic Manuscript Formatter

> **Codex Verdict (March 2026):** Feature-rich but operationally unstable. The repository has ~90% file coverage but needs runtime validation across all 34 routes. Phase 0 (restore truth & fast feedback) is complete.

ScholarForm AI formats academic manuscripts into publisher-ready outputs using deterministic rules plus AI-assisted analysis. It also generates full research documents through AI Agent and Multi-Doc Synthesis modes.

## Quick Links

- **Frontend:** `http://localhost:3000` (Next.js 14)
- **Backend API:** `http://localhost:8000` — Swagger at `http://localhost:8000/docs`
- **OpenAPI Schema:** `http://localhost:8000/openapi.json`
- **Framework:** Next.js 14 (App Router), **NOT** Vite
- **Python:** 3.12.x (pinned)
- **Routes:** 34 pages in `frontend/src/app/`

---

## AI/ML Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Classifier | SciBERT (`allenai/scibert_scivocab_uncased`) | Section/semantic classification (disabled by default) |
| LLM Tier 1 | NVIDIA NIM — Llama 3.3 70B Instruct | Primary cloud inference |
| LLM Tier 2 | **Groq** — llama-3.3-70b-versatile | Fast free-tier fallback |
| LLM Tier 3 | DeepSeek R1 via Ollama | Local/offline fallback |
| Embeddings | BGE-M3 / multi-qa-MiniLM-L6-v2 | RAG style-rule retrieval |
| PDF Parser | GROBID → Docling → PyMuPDF | 3-tier fallback (Render 512MB constraint) |

> **Note:** GROBID Docker requires 1.5GB RAM — incompatible with Render free tier. The 3-tier PDF fallback (Docling → PyMuPDF → PyPDF2) is the production path.

---

## Required Environment Variables

### Backend (`backend/.env`)

```env
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJhbG...
SUPABASE_ANON_KEY=eyJhbG...
SUPABASE_JWT_SECRET=...
SUPABASE_SERVICE_ROLE_KEY=...
NVIDIA_API_KEY=nvapi-...
GROQ_API_KEY=gsk_...
REDIS_URL=redis://localhost:6379
GROBID_ENABLED=false            # true only if GROBID Docker is running locally
FORCE_HTTPS=true
ENABLE_FILE_CLEANUP=true
USE_SCIBERT_CLASSIFICATION=false
LOW_MEMORY_MODE=true            # Render 512MB profile
PRELOAD_AI_MODELS=false         # avoid startup model warmup
RAG_USE_TRANSFORMERS=false      # deterministic lightweight embeddings
DEFAULT_FAST_MODE=true          # disables heavy optional stages unless requested
CROSSREF_MAX_WORKERS=1
LLM_CACHE_TTL_SECONDS=3600
CLAMAV_HOST=localhost:3310
```

### Frontend (`frontend/.env.local`)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbG...
```

> **Important:** All frontend env vars are prefixed `NEXT_PUBLIC_*` — not `VITE_*`.

### Syncing Templates
If you've added new environment variables to the code, sync the template files automatically:
```bash
python scripts/generate_env_template.py
```
This scans the codebase and generates:
- `backend/.env.template`
- `frontend/.env.template`

To also sync `.env.example` files with discovered keys:
```bash
python scripts/generate_env_template.py --sync-examples
```

---

## Quick Setup

### 1. Backend (Python 3.12 required)

```bash
cd backend

# Windows
python -m venv .venv
.venv\Scripts\activate

# Mac/Linux
python3.12 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

Set backend env vars in `backend/.env`, then start:

```bash
uvicorn app.main:app --reload --port 8000
```

API docs: `http://localhost:8000/docs`

> **Python version:** Must be **3.12.x**. Python 3.11.9 causes pytest import collisions. Verify with `python --version`.

### 2. Frontend (Node 18+ required)

```bash
cd frontend
npm install
npm run dev
```

Open: `http://localhost:3000`

---

## Core API Endpoints (34 routes total)

| Method | Endpoint | Purpose |
|--------|---------|---------|
| `POST` | `/api/v1/documents/upload` | Upload & format document |
| `GET` | `/api/v1/documents/{job_id}/status` | Poll processing status |
| `GET` | `/api/v1/documents/{job_id}/preview` | Rendered HTML preview |
| `GET` | `/api/v1/documents/{job_id}/compare` | Before/after diff |
| `GET` | `/api/v1/documents/{job_id}/download` | Download DOCX/PDF |
| `POST` | `/api/v1/documents/{job_id}/edit` | Save edits |
| `GET` | `/api/v1/templates` | List all 17 templates |
| `GET` | `/api/v1/health` | Health check (Redis, DB, ChromaDB) |
| `GET` | `/metrics` | Prometheus metrics |

See [`docs/API.md`](docs/API.md) for the complete endpoint reference.

---

## Architecture

- **Frontend:** Next.js 14 (App Router) on Vercel
- **Backend:** FastAPI + Uvicorn on Render
- **Gateway:** FastAPI only — no Spring Boot gateway (the Spring Boot gateway in earlier plans is **obsolete/incorrect**)
- **Realtime:** Redis pub/sub → WebSocket / SSE
- **Data:** Supabase (PostgreSQL) + Supabase Storage + ChromaDB (RAG)

See [`docs/architecture.md`](docs/architecture.md) for the full system diagram.

---

## Running Tests

**Backend (fast, no external services):**
```bash
cd backend
pytest tests -m "not integration and not llm" -x -q
```

**Frontend:**
```bash
cd frontend
npm test
```

**E2E (Playwright, requires running backend):**
```bash
npx playwright test tests/e2e/upload.spec.js --headed
```

See [`docs/Testing.md`](docs/Testing.md) for the full test strategy.

---

## Pre-commit Hooks (Ruff + ESLint)

Pre-commit is configured in `.pre-commit-config.yaml` to run:

- `ruff` + `ruff-format` on backend Python files
- `eslint` on frontend JS/TS files

Install and enable once:

```bash
pip install pre-commit
pre-commit install
```

Windows one-liner bootstrap:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup_precommit.ps1
```

Run manually across the full repository:

```bash
pre-commit run --all-files
```

Notes:

- `frontend-eslint` lints only staged frontend files via `scripts/run_frontend_eslint_precommit.py`; ensure frontend deps are installed (`cd frontend && npm install`).
- `ruff` hook uses `--fix`, and if it rewrites files the commit exits non-zero so you can review and re-stage changes.

---

## Analytics (PostHog Free Tier)

Frontend analytics is opt-in via env vars:

```env
NEXT_PUBLIC_POSTHOG_KEY=phc_xxx
NEXT_PUBLIC_POSTHOG_HOST=https://app.posthog.com
```

When configured, the app captures:

- `upload_started`
- `upload_completed`
- `generator_session_started`
- `$pageview`

If PostHog is not configured, analytics calls are no-ops and do not block user flows.
