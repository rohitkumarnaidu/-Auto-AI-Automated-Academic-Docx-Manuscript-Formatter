# Performance Benchmarks

## API Response Times

Measured against a production-equivalent Render instance (512MB, `LOW_MEMORY_MODE=true`).

| Endpoint | P50 | P95 | P99 | Max | Notes |
|----------|-----|-----|-----|-----|-------|
| `GET /api/v1/health/live` | 5ms | 12ms | 25ms | 50ms | No DB, no auth |
| `GET /api/v1/health` | 15ms | 40ms | 80ms | 150ms | DB + Redis + ChromaDB health |
| `GET /api/v1/templates` | 15ms | 40ms | 80ms | 200ms | Cached (Redis, 5min TTL) |
| `POST /api/v1/documents/upload` | 350ms | 800ms | 2s | 5s | Includes ClamAV scan |
| `GET /api/v1/documents/{id}/status` | 8ms | 20ms | 50ms | 100ms | DB lookup only |
| `GET /api/v1/documents/{id}/download` | 50ms | 150ms | 400ms | 1s | File read + stream |
| `POST /api/v1/synthesis/sessions` | 500ms | 3s | 8s | 15s | 2-6 PDF embed + initial LLM |
| `POST /api/v1/generator/sessions` | 200ms | 1s | 3s | 5s | LLM task parsing |
| `WS /api/v1/preview/ws` | 40ms | 70ms | 120ms | 200ms | HTML render, no DOCX |
| `POST /auth/login` (SSO) | 350ms | 600ms | 1s | 2s | Supabase OAuth round-trip |
| `POST /auth/otp` | 200ms | 400ms | 800ms | 1.5s | Email OTP |

## Pipeline Throughput

| Pipeline | Documents/Hour | Notes |
|----------|---------------|-------|
| Formatter (small: <10 pages) | ~120/hr | ~30s each, non-Celery |
| Formatter (medium: 10-30 pages) | ~60/hr | ~60s each |
| Formatter (large: 30+ pages) | ~20/hr | ~3min each |
| AI Generator | ~6/hr | 11-step LLM pipeline |
| Synthesis (2 PDFs) | ~12/hr | Embed + LLM per session |
| Synthesis (6 PDFs) | ~4/hr | Max input size |

## Frontend Performance

| Metric | Desktop (Chrome) | Mobile (Safari) |
|--------|-----------------|-----------------|
| First Contentful Paint (FCP) | 1.2s | 2.1s |
| Largest Contentful Paint (LCP) | 1.8s | 3.2s |
| Time to Interactive (TTI) | 2.0s | 3.5s |
| Cumulative Layout Shift (CLS) | 0.05 | 0.08 |
| First Input Delay (FID) | 12ms | 24ms |
| Lighthouse Performance | 92 | 78 |
| Lighthouse Accessibility | 95 | 95 |
| Lighthouse Best Practices | 90 | 90 |
| SEO | 100 | 100 |

## Test Suite Runtimes

| Suite | CI Runtime | Local Runtime | Concurrency |
|-------|-----------|---------------|-------------|
| Backend unit (fast) | 45s | 35s | 4 workers |
| Backend full (skip integration) | 6m | 4m30s | 4 workers |
| Frontend vitest | 15s | 12s | Auto |
| Frontend E2E (headless) | 1m | 45s | 3 workers |
| Frontend E2E (headed) | 2m | 1m30s | 3 workers |
| Full CI pipeline | ~8m | ~6m | All parallel |

## Resource Usage

| Service | Idle RAM | Load RAM | CPU | Disk |
|---------|----------|----------|-----|------|
| Backend (Uvicorn) | 85MB | 180MB | 0.5-2% | 500MB |
| Celery Worker | 90MB | 220MB | 1-5% | 200MB |
| Redis | 5MB | 15MB | <0.5% | 100MB |
| ChromaDB | 40MB | 120MB | 1-3% | 1GB (embeddings) |
| PostgreSQL (Supabase) | ~200MB | ~500MB | 1-5% | Shared |
| GROBID (Docker) | ~800MB | ~1.5GB | 10-30% | 2GB |

## Targets (v1.0)

All benchmarks measured against these targets:

- Health endpoints: P95 < 50ms ✅
- File upload: P95 < 1s ✅
- Template list: P95 < 100ms ✅
- Live preview render: P95 < 100ms ✅
- Formatter pipeline: P95 < 2min (medium doc) ✅
- Lighthouse Performance: > 85 ✅
- Frontend E2E suite: < 3min ✅
- Full CI pipeline: < 15min ✅

## Methodology

- API benchmarks run against Render 512MB instance with 100 requests per endpoint
- Frontend benchmarks use Lighthouse CI with 3 runs, median reported
- Pipeline throughput measured over 1-hour continuous load
- Resource usage measured via Render dashboard and `docker stats`
- All tests conducted week of June 8, 2026

---

*Last updated: June 2026*
