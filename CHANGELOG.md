# Changelog

All notable changes to ScholarForm AI are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] — 2026-06-13

### Added
- Document formatter pipeline (12-stage: parse, structure, classify, NLP, validate, format, export)
- 17 built-in journal templates (IEEE, APA, ACM, Springer, Elsevier, Nature, Harvard, Chicago, MLA, Vancouver, Numeric, Modern Blue, Modern Gold, Modern Red, None, Resume, Portfolio)
- AI Agent generator (11-step pipeline: task parsing, outline, writing, citations, quality, export)
- Multi-doc synthesis engine (ChromaDB RAG, SSE streaming, 2-6 PDF input)
- Live preview WebSocket editor with <80ms render target
- Supabase Auth (JWT, OTP, OAuth Google/GitHub)
- API key management with Fernet encryption
- Stripe billing integration
- TipTap rich text editor on `/edit` page
- Dark/light mode with unified ThemeToggle
- Onboarding tour for new users
- Guest upload flow (5/day limit)

### Security
- ClamAV virus scanning on uploads
- JWKS JWT verification against Supabase
- Two-layer rate limiting (base + tier-aware)
- CSP/HSTS security headers middleware
- Abuse detection middleware
- RBAC middleware (stub — expanded in v1.1)
- Audit logging (minimal — expanded in v1.1)
- MIME + magic byte + extension tri-validation
- Request ID correlation on all endpoints

### Infrastructure
- FastAPI backend with Uvicorn on Render
- Next.js 16 (App Router) frontend on Vercel
- Celery background workers with Redis broker
- ChromaDB vector store for RAG
- Alembic database migrations
- 3-tier PDF parsing fallback (GROBID → Docling → PyMuPDF)
- 3-tier LLM fallback (NVIDIA NIM → Groq → Ollama)
- CI/CD: ruff, mypy, pytest, ESLint, vitest, Playwright
- Pre-commit hooks (ruff, eslint, detect-secrets)
- Docker Compose for local development

### Documentation
- Enterprise-grade docs overhaul (88 files)
- YAML frontmatter on all documentation
- docs/README.md index portal
- Architecture Decision Records (10 ADRs)
- GLOSSARY.md terminology reference
- cheatsheet.md quick-reference card
- .docs-style-guide.md for contributors
- Mermaid diagrams in architecture and deployment docs
- CI freshness check for documentation staleness
- SECURITY.md vulnerability disclosure policy
- CHANGELOG.md (this file)

### Fixed
- Python 3.12 pin for backend (resolved pytest import collision)
- React 19 / Next.js 16 version alignment
- Vite → Next.js references across all docs
- E2E test stability (auth/landing/dark-mode/selector fixes)
- Empty `docs/security/` directory removed
- Absolute `file:///C:/...` paths replaced with relative
- Dashboard URL placeholders marked as not-yet-deployed
- API.md curl examples added for all endpoints

---

## [0.9.0] — 2026-03-18

### Added
- Initial public beta release
- Core formatter pipeline with 8-stage processing
- 15 journal templates
- Basic auth (Supabase JWT)
- SSE progress streaming
- Frontend with 34 App Router routes

### Known Issues (v0.9)
- Python 3.11.9 caused pytest import collision — required 3.12
- 93 E2E test files existed but most were <700B stubs
- RBAC middleware was 708B stub
- Audit logging was 1.1KB minimal
- LaTeX exporter was 743B stub
- api.synthesis.js was 36B empty stub
- deploy-staging.yml missing
- Grafana dashboards not set up
