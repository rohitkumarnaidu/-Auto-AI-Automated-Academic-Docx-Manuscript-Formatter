# ScholarForm AI — Deployment Guide

> **Last Updated:** March 2026 (Codex 5.4 Audit)  
> **Critical Note:** The original plan assumed GROBID Docker was always available. Render free tier has a **512MB RAM** constraint; GROBID Docker requires **1.5GB RAM**. The production PDF parsing strategy uses the 3-tier fallback below.

---

## Recommended Free-Tier Stack

| Component | Host | Why |
|-----------|------|-----|
| Frontend | **Vercel** | Native Next.js 14 support, SSR, edge functions, free tier |
| Backend | **Render** | Docker support, free tier with 750 hrs/mo |
| PostgreSQL | **Supabase** | Free tier, built-in auth, 500MB |
| Redis | **Upstash** | Free tier, serverless, 10K commands/day |
| ChromaDB | **Render** (private service) | Co-located with backend |
| ClamAV | **Render Docker** ⚠️ | 512MB constraint — may fail; add graceful skip |
| GROBID | **Render Docker** ❌ | Needs 1.5GB RAM — use Docling fallback instead |

---

## PDF Parsing Fallback Strategy ($0 Solution)

**Do NOT rely on GROBID on Render free tier.** Use the 3-tier fallback:

| Tier | Tool | Activation | Cost |
|------|------|------------|------|
| 1 | GROBID | `GROBID_ENABLED=true` (local dev only) | $0 (local Docker) |
| 2 | **Docling** | Default when GROBID disabled | $0 (Python package) |
| 3 | PyMuPDF / PyPDF2 | Last-resort fallback | $0 (Python package) |

Set `GROBID_ENABLED=false` on all cloud deployments unless you have a paid Render instance with ≥2GB RAM.

---

## Alternative Hosts

| Alternative | For |
|-------------|-----|
| Railway | Backend + Redis (easy Docker deploys, $5/mo) |
| Fly.io | Backend (edge regions, $0-7/mo) |
| GitHub Pages | Static marketing page only |
| Hugging Face Spaces | SciBERT model endpoints / ML demos |
| Netlify | Frontend (if not using SSR heavily) |

---

## Docker Compose (Local Development)

```yaml
version: '3.9'
services:
  frontend:
    build: ./frontend
    ports: ['3000:3000']    # NOT 5173 — this is Next.js, not Vite
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
      - NEXT_PUBLIC_SUPABASE_URL=${SUPABASE_URL}
      - NEXT_PUBLIC_SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}

  fastapi:
    build: ./backend
    ports: ['8000:8000']
    env_file: ./backend/.env

  redis:
    image: redis:7-alpine
    ports: ['6379:6379']

  grobid:
    image: lfoppiano/grobid:0.8.0
    ports: ['8070:8070']
    # ⚠️ Only include locally — requires 1.5GB RAM

  clamav:
    image: clamav/clamav
    ports: ['3310:3310']

  prometheus:
    image: prom/prometheus
    ports: ['9090:9090']
```

---

## Environment Variables

### Backend (`backend/.env`)

```env
# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJhbG...
SUPABASE_ANON_KEY=eyJhbG...
SUPABASE_JWT_SECRET=...
SUPABASE_SERVICE_ROLE_KEY=...

# LLM Providers
NVIDIA_API_KEY=nvapi-...
GROQ_API_KEY=gsk_...            # Required for Tier 2 fallback

# Infrastructure
REDIS_URL=redis://localhost:6379
FORCE_HTTPS=true
ENABLE_FILE_CLEANUP=true
LLM_CACHE_TTL_SECONDS=3600

# PDF Parsing
GROBID_ENABLED=false            # ← Set false on Render free tier
GROBID_URL=http://localhost:8070

# AI/ML
USE_SCIBERT_CLASSIFICATION=false   # ← Keep false — SciBERT is too large for free tier

# Security
CLAMAV_HOST=localhost:3310
STRIPE_WEBHOOK_SECRET=whsec_...

# Render-specific
PORT=8000
```

### Frontend (`frontend/.env.local`)

```env
# All frontend vars MUST start with NEXT_PUBLIC_ (not VITE_)
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbG...
```

---

## Deployment Checklist

### Pre-Deploy
- [ ] Set `FORCE_HTTPS=true` in backend env
- [ ] Set `GROBID_ENABLED=false` on Render free tier
- [ ] Verify all `NEXT_PUBLIC_*` env vars are set on Vercel
- [ ] Run `alembic upgrade head` on production database
- [ ] Add `GROQ_API_KEY` for LLM Tier 2 fallback

### Deploy
- [ ] Deploy backend to Render (Docker)
- [ ] Deploy frontend to Vercel
- [ ] Verify health check: `GET /api/v1/health`
- [ ] Test: `{"status": "ok", "services": {"redis": "ok", "db": "ok"}}`

### Post-Deploy
- [ ] Test guest upload flow end-to-end
- [ ] Verify Stripe webhook URL is configured (use Stripe CLI)
- [ ] Test `/api/v1/templates` returns all 17 templates
- [ ] Test SSE streaming on `/api/v1/generator/sessions/{id}/events`
- [ ] Set up DNS for custom domain
- [ ] Enable branch protection on GitHub

---

## Render-Specific Constraints

| Constraint | Impact | Mitigation |
|-----------|--------|-----------|
| 512MB RAM free tier | GROBID fails | Use Docling fallback (`GROBID_ENABLED=false`) |
| Cold starts (30+ seconds) | First request after idle | Add keep-alive ping or upgrade to paid tier |
| Free tier sleeps after 15min | Delays for users | Use Render paid ($7/mo) or keep-alive cron |

---

## Missing Deployment Artifacts

| Artifact | Status | Priority |
|----------|--------|---------|
| `deploy-staging.yml` | ❌ **Missing** | 🔴 HIGH — create before first deploy |
| Grafana dashboards | ❌ **Missing** | 🔴 HIGH — no monitoring otherwise |
| `ops/` configuration directory | ❌ **Missing** | 🟡 MEDIUM |
