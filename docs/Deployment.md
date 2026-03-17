# ScholarForm AI — Deployment Guide

## Recommended Free-Tier Stack

| Component | Host | Why |
|-----------|------|-----|
| Frontend | **Vercel** | Native Next.js support, SSR, edge functions |
| Backend | **Render** | Docker support, free tier with 750 hrs/mo |
| PostgreSQL | **Supabase** | Free tier, built-in auth, 500MB |
| Redis | **Upstash** | Free tier, serverless, 10K commands/day |
| ChromaDB | **Render** (private service) | Co-located with backend |
| ClamAV | **Render** (Docker) | Security requirement |
| GROBID | **Render** (Docker) | PDF parsing |

## Alternative Hosts
| Alternative | For |
|-------------|-----|
| Railway | Backend + Redis (easy Docker deploys) |
| Fly.io | Backend (edge regions) |
| GitHub Pages | Static marketing page only |
| Hugging Face Spaces | SciBERT demo / ML model endpoints |
| Netlify | Frontend (if not using SSR heavily) |

## Docker Compose (Development)
```yaml
version: '3.9'
services:
  frontend:    build: ./frontend        ports: ['3000:3000']
  fastapi:     build: ./backend         ports: ['8000:8000']
  redis:       image: redis:7-alpine    ports: ['6379:6379']
  grobid:      image: lfoppiano/grobid:0.8.0  ports: ['8070:8070']
  clamav:      image: clamav/clamav     ports: ['3310:3310']
  prometheus:  image: prom/prometheus   ports: ['9090:9090']
```

## Environment Variables

### Backend (.env)
```
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJhbG...
NVIDIA_API_KEY=nvapi-...
GROQ_API_KEY=gsk_...
REDIS_URL=redis://localhost:6379
FORCE_HTTPS=true
ENABLE_FILE_CLEANUP=true
USE_SCIBERT_CLASSIFICATION=false
LLM_CACHE_TTL_SECONDS=3600
CLAMAV_HOST=localhost:3310
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbG...
```

## Deployment Checklist
- [ ] Set FORCE_HTTPS=true
- [ ] Verify all env vars are set
- [ ] Run `alembic upgrade head` on database
- [ ] Verify health check: GET /api/v1/health
- [ ] Test guest upload flow end-to-end
- [ ] Verify Stripe webhook URL is configured
- [ ] Set up DNS for custom domain
- [ ] Enable branch protection on GitHub
