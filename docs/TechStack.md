# ScholarForm AI — Technology Stack

> **Last Updated:** March 2026 | Reflects Codex 5.4 Audit findings

---

## Frontend

| Tech | Version | Purpose |
|------|---------|---------|
| **Next.js** | 14 (App Router) | SSR, routing, API routes — **NOT Vite** |
| React | 18+ | UI components |
| Tailwind CSS | 3.4.19 | Utility-first styling |
| TipTap | @tiptap/react | Rich text editor (confirmed on `/edit` and `/formatter/live`) |
| Framer Motion | Latest | Animations (token streaming, slide-ins) |
| react-resizable-panels | Latest | Split editor panels |
| react-dropzone | Latest | File upload drag-and-drop |
| Supabase JS | Latest | Auth, DB client |
| **@testing-library/dom** | Latest | **Required** for vitest unit tests (common missing-dep failure) |
| Vitest | Latest | Unit testing for React hooks and pages |
| Playwright | Latest | E2E testing (93 test files, many are stubs) |
| ESLint | Latest | Linting |

> **Env vars:** All frontend environment variables use the `NEXT_PUBLIC_*` prefix. No `VITE_*` variables exist.  
> **Dev server port:** `3000` (not `5173` — that was a Vite default and is now stale).

---

## Backend

| Tech | Version | Purpose |
|------|---------|---------|
| **Python** | **3.12.x (pinned)** | Runtime — 3.11.9 causes pytest import collisions |
| FastAPI | Latest | API framework (**sole gateway** — no Spring Boot) |
| Uvicorn | Latest | ASGI server |
| Celery | Latest | Background task queue |
| Redis (aioredis) | 7 | Cache, pub/sub, queue broker |
| python-docx | Latest | DOCX generation |
| docxtpl | Latest | Jinja2 DOCX templates |
| Pandoc | Latest | LaTeX conversion (stub — needs full impl) |
| python-clamd | Latest | Virus scanning (ClamAV) |
| LiteLLM | Latest | Multi-LLM provider abstraction (NVIDIA → Groq → Ollama) |
| Prometheus client | Latest | Metrics instrumentation |
| Alembic | Latest | Database migrations |
| ChromaDB | Latest | Vector embeddings for RAG |
| sentence-transformers | Latest | Embedding model (multi-qa-MiniLM-L6-v2) |
| Docling | Latest | High-quality PDF/OCR fallback structure extraction |
| pytest | Latest | Backend testing |

> **Python version enforcement:** Backend `Dockerfile` and `.python-version` pin to `3.12`. Verify with `python --version` before running tests.

---

## LLM Providers (Tiered Fallback)

| Tier | Provider | Model | Notes |
|------|----------|-------|----|
| 1 | NVIDIA NIM | meta/llama-3.3-70b-instruct | Primary cloud inference |
| 2 | **Groq** | llama-3.3-70b-versatile | Fast free-tier secondary (Codex-confirmed implemented) |
| 3 | Ollama | deepseek-r1 | Local/offline fallback |
| 4 (Future) | vLLM | Llama-3.1-8B | Self-hosted GPU inference |

---

## PDF Parsing (3-Tier Fallback)

The original plan assumed GROBID Docker would always be available. Render free tier has a 512MB RAM constraint; GROBID requires 1.5GB.

| Tier | Tool | Condition |
|------|------|-----------|
| 1 | GROBID | Only if `GROBID_ENABLED=true` and local Docker running |
| 2 | Docling | Default production path on Render free tier |
| 3 | PyMuPDF / PyPDF2 | Last-resort fallback for simple text extraction |

---

## Infrastructure

| Service | Provider | Purpose |
|---------|----------|---------|
| Frontend Hosting | Vercel | Next.js hosting (SSR, edge functions) |
| Backend Hosting | Render | FastAPI + workers (512MB RAM free tier) |
| Database | Supabase (PostgreSQL) | Users, jobs, sessions |
| File Storage | Supabase Storage | Uploaded/generated files |
| Cache/Queue | Upstash Redis | LLM cache, Celery broker, pub/sub |
| Vector DB | ChromaDB (Render) | RAG embeddings |
| Virus Scanner | ClamAV (Docker) | Upload scanning |
| PDF Parser | Docling (primary) / GROBID (optional) | Scientific PDF extraction |

---

## Monitoring

| Tool | Status | Purpose |
|------|--------|---------|
| Prometheus | ✅ Implemented | Metrics via `prometheus_metrics.py` (7KB) |
| Grafana | ❌ Not yet set up | Dashboard visualization |
| Structured logging | ✅ Partial | `logging_context.py` (3.4KB) |
| Sentry.io | 📋 Planned | Error tracking before prod |

---

## CI/CD

| Workflow | Purpose |
|----------|---------|
| `backend-ci.yml` | Ruff + mypy + pytest |
| `frontend-ci.yml` | ESLint + build |
| `security.yml` | Trivy + Bandit + OWASP |
| `deploy-production.yml` | Production deployment |
| `e2e-production.yml` | E2E tests |
| `deploy-staging.yml` | ❌ **Missing** — must be created |

---

## Route Count

| Source | Frontend Routes |
|--------|----------------|
| Original master plan | 25 routes |
| **Codex-verified reality** | **34 routes** in `frontend/src/app/` |
