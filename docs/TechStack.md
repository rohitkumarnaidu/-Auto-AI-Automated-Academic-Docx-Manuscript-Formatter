# ScholarForm AI — Technology Stack

## Frontend
| Tech | Version | Purpose |
|------|---------|---------|
| Next.js | 14 (App Router) | SSR, routing, API routes |
| React | 18+ | UI components |
| Tailwind CSS | 3.4.19 | Utility-first styling |
| TipTap | @tiptap/react | Rich text editor (live preview, /edit) |
| Framer Motion | Latest | Animations (token streaming, slide-ins) |
| react-resizable-panels | Latest | Split editor panels |
| react-dropzone | Latest | File upload drag-and-drop |
| Supabase JS | Latest | Auth, DB client |
| Playwright | Latest | E2E testing |
| Next.jsst | Latest | Unit testing |
| ESLint | Latest | Linting |

## Backend
| Tech | Version | Purpose |
|------|---------|---------|
| Python | **3.12.x** (pinned) | Runtime |
| FastAPI | Latest | API framework |
| Uvicorn | Latest | ASGI server |
| Celery | Latest | Background task queue |
| Redis (aioredis) | 7 | Cache, pub/sub, queue broker |
| python-docx | Latest | DOCX generation |
| docxtpl | Latest | Jinja2 DOCX templates |
| Pandoc | Latest | LaTeX conversion |
| python-clamd | Latest | Virus scanning |
| LiteLLM | Latest | Multi-LLM provider abstraction |
| Prometheus client | Latest | Metrics instrumentation |
| Alembic | Latest | Database migrations |
| ChromaDB | Latest | Vector embeddings for RAG |
| sentence-transformers | Latest | Embedding model (multi-qa-MiniLM-L6-v2) |
| pytest | Latest | Testing |

## LLM Providers (Tiered Fallback)
| Tier | Provider | Model | Purpose |
|------|----------|-------|---------|
| 1 | NVIDIA NIM | meta/llama-3.3-70b-instruct | Primary (cloud) |
| 2 | Groq | llama-3.3-70b-versatile | Fast secondary (free tier) |
| 3 | Ollama | deepseek-r1 | Local/offline fallback |
| 4 (Future) | vLLM | Llama-3.1-8B | Self-hosted GPU inference |

## Infrastructure
| Service | Provider | Purpose |
|---------|----------|---------|
| Frontend Hosting | Vercel | Next.js hosting |
| Backend Hosting | Render | FastAPI + workers |
| Database | Supabase (PostgreSQL) | Users, jobs, sessions |
| File Storage | Supabase Storage | Uploaded/generated files |
| Cache/Queue | Upstash Redis | LLM cache, Celery broker, pub/sub |
| Vector DB | ChromaDB (Render) | RAG embeddings |
| Virus Scanner | ClamAV (Docker) | Upload scanning |
| PDF Parser | GROBID (Docker) | Scientific PDF extraction |

## Monitoring
| Tool | Purpose |
|------|---------|
| Prometheus | Metrics collection |
| Grafana | Dashboard visualization (NOT YET SET UP) |
| Structured logging | Request tracing |

## CI/CD
| Workflow | Purpose |
|----------|---------|
| backend-ci.yml | Ruff + mypy + pytest |
| frontend-ci.yml | ESLint + build |
| security.yml | Trivy + Bandit + OWASP |
| deploy-production.yml | Production deployment |
| e2e-production.yml | E2E tests |
