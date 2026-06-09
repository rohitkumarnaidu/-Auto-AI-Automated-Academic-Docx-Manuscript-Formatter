# ScholarForm AI — Developer Onboarding Guide

**Last Updated:** May 21, 2026  
**Audience:** New developers joining the ScholarForm AI team

---

## Quick Start (15 minutes)

### 1. Clone & Setup
```bash
git clone https://github.com/scholarform/automated-manuscript-formatter.git
cd automated-manuscript-formatter

# Backend
cd backend
python -m venv .venv && source .venv/bin/activate  # Linux/Mac
python -m venv .venv && .venv\Scripts\activate     # Windows
pip install -r requirements-dev.txt

# Frontend
cd ../frontend
npm install
```

### 2. Environment Variables
```bash
# Copy example env files
cp backend/.env.example backend/.env
cp frontend/.env.local.example frontend/.env.local

# Minimum required for local dev:
# backend/.env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_DB_URL=postgresql://...
SECRET_KEY=your-secret-key
```

### 3. Run Locally
```bash
# Backend
cd backend
uvicorn app.main:app --reload --port 8000

# Frontend (in another terminal)
cd frontend
npm run dev
```

### 4. Verify
- Backend: http://localhost:8000/docs (Swagger UI)
- Frontend: http://localhost:3000
- Health: http://localhost:8000/api/v1/health/live

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │ Formatter│  │ Generator│  │ Admin Dashboard  │  │
│  └────┬─────┘  └────┬─────┘  └────────┬─────────┘  │
│       └──────────────┼────────────────┘             │
│                      │ REST API                     │
└──────────────────────┼──────────────────────────────┘
                       │
┌──────────────────────┼──────────────────────────────┐
│              Backend (FastAPI)                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │Documents │  │Templates │  │ API Key Manager  │  │
│  └────┬─────┘  └────┬─────┘  └────────┬─────────┘  │
│       └──────────────┼────────────────┘             │
│                      │                              │
│  ┌───────────────────┼──────────────────────────┐  │
│  │           Pipeline Engine                    │  │
│  │  Parse → Normalize → Analyze → Format → Export│ │
│  └───────────────────┼──────────────────────────┘  │
└──────────────────────┼──────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
   ┌────┴────┐   ┌────┴────┐   ┌────┴────┐
   │Supabase │   │  Redis  │   │  LLMs   │
   │(Postgres│   │ (Cache) │   │(OpenAI, │
   │  + Auth)│   │         │   │Anthropic│
   └─────────┘   └─────────┘   │ etc.)   │
                               └─────────┘
```

---

## Key Directories

| Path | Purpose |
|------|---------|
| `backend/app/routers/v1/` | API endpoint definitions |
| `backend/app/services/` | Business logic services |
| `backend/app/pipeline/` | Document processing pipeline |
| `backend/app/models/` | SQLAlchemy ORM models |
| `backend/app/middleware/` | HTTP middleware |
| `backend/tests/` | Backend test suite |
| `frontend/app/` | Next.js App Router pages |
| `frontend/src/components/` | React components |
| `frontend/src/services/` | API client services |
| `frontend/e2e/` | Playwright E2E tests |

---

## Development Workflow

### 1. Create a Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Write Code + Tests
```bash
# Backend tests
cd backend
pytest tests/test_your_feature.py -v

# Frontend tests
cd frontend
npx vitest run

# E2E tests (requires running server)
npx playwright test
```

### 3. Pre-commit Checks
```bash
# Linting
ruff check backend/app/
ruff format backend/app/

# Type checking
mypy backend/app/

# Frontend linting
cd frontend
npm run lint
npx tsc --noEmit
```

### 4. Commit & Push
```bash
git add .
git commit -m "feat: add your feature description"
git push origin feature/your-feature-name
```

### 5. Create PR
- Link to relevant issue
- Include test results
- Request review from 2 team members

---

## API Documentation

### Swagger UI
- Local: http://localhost:8000/docs
- Staging: https://staging.scholarform.ai/docs
- Production: https://api.scholarform.ai/docs

### Key Endpoints
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/documents/upload` | Upload document for formatting |
| GET | `/api/v1/templates` | List available templates |
| POST | `/api/v1/generator/sessions` | Create AI generation session |
| POST | `/api/v1/keys` | Add user API key |
| GET | `/api/v1/keys/usage` | View API key usage |
| GET | `/api/v1/health/live` | Health check |

---

## Troubleshooting

### Common Issues

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements-dev.txt` |
| `SUPABASE_DB_URL not set` | Copy `.env.example` and fill in values |
| CORS errors | Check `ALLOWED_ORIGINS` in backend `.env` |
| Frontend build fails | Delete `node_modules` and `npm install` |
| Tests hang | Check if Supabase/Redis is reachable |

### Getting Help
- **Slack:** `#scholarform-dev`
- **Issues:** https://github.com/scholarform/automated-manuscript-formatter/issues
- **Docs:** https://docs.scholarform.ai
- **On-call:** Check PagerDuty rotation

---

## Production Access

### Request Access
1. Get approval from engineering lead
2. Request Supabase project access
3. Request Render dashboard access
4. Request AWS/GCP console access (if applicable)

### Deployment
```bash
# Deploy to staging
git push origin main  # Triggers staging CI/CD

# Deploy to production (requires approval)
# Via GitHub: Create release → Approve in GitHub Environments
```
