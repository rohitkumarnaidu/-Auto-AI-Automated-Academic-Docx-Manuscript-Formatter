# Risk Register

> **Last Updated:** March 2026  
> **Sources:** Codex 5.4 Audit (15 risks) + Antigravity comprehensive audit risk map  
> **Format:** Red (HIGH impact/likelihood) → Yellow (MEDIUM) → Green (LOW/managed)

---

## 🔴 Red — High Impact / High Likelihood

| # | Risk | Details | Mitigation Status |
|---|------|---------|-----------------|
| R-01 | **Infrastructure RAM Constraint** | Render free tier = 512MB RAM. GROBID Docker requires 1.5GB. Incompatible. | ✅ **Mitigated** — 3-tier PDF fallback: Docling → PyMuPDF → PyPDF2. `GROBID_ENABLED=false` on Render. |
| R-02 | **Python Version Mismatch** | Python 3.11.9 causes pytest import collisions — `pytest` module shadows stdlib. | ✅ **Mitigated** — Pin to Python 3.12 in Dockerfile + `.python-version`. Verify with `python --version`. |
| R-03 | **WebSocket Disconnects (Live Editor)** | `/formatter/live` relies on a WebSocket that may drop during Render scaling or timeout thresholds. Cold starts on free tier add latency. | ⚠️ **In Progress** — Implement exponential backoff + reconnection queue in `useLivePreviewSocket.js`. Needs QA. |
| R-04 | **No Staging Environment** | `deploy-staging.yml` is missing. No automatic staging deploy on merge to `main`. | ❌ **Not mitigated** — Create `deploy-staging.yml` before first production deploy. |
| R-05 | **E2E Tests are Stubs** | 93 E2E test files; most are <700 bytes with no real assertions. No confidence in pipeline coverage. | ⚠️ **In Progress** — Fill top 20 critical path tests with real DOM assertions. |
| R-06 | **RBAC is a Stub** | `rbac.py` is 708 bytes — insufficient to enforce admin/pro/free/guest roles on any endpoint. | ❌ **Not mitigated** — Must be expanded before production. |
| R-07 | **No Monitoring** | Prometheus middleware exists; Grafana dashboards do NOT. Operating blind in production. | ❌ **Not mitigated** — Set up at minimum one Grafana dashboard for request rate + error rate. |

---

## 🟡 Yellow — Medium Impact / Manageable Likelihood

| # | Risk | Details | Mitigation Status |
|---|------|---------|-----------------|
| R-08 | **Template Sync Drift** | Frontend template whitelist is statically defined rather than sourced from `/api/v1/templates`. Can get out of sync. | ⚠️ **Planned** — Phase 3 will source template list from API endpoint. |
| R-09 | **UI Component Consistency** | `frontend/components/` vs `frontend/src/components/` dual-directory existence. Violet accent drift across live preview components. 3 icon libraries mixed. | ⚠️ **In Progress** — Directory consolidation needed. Design system token guide needed. |
| R-10 | **Subprocess Attack Surface** | Pandoc/LibreOffice subprocesses invoked for conversion carry command injection risk with malicious inputs. | ⚠️ **Partial** — Input whitelist exists; subprocess args sanitization needs explicit audit. |
| R-11 | **LLM Rate Limits (Groq Free Tier)** | Groq free tier has 100K tokens/day limit. High usage can exhaust the fallback tier before Ollama kicks in. | ⚠️ **Partial** — `LLM_CACHE_TTL_SECONDS=3600` provides caching. Aggressive caching needed for repeated prompts. |
| R-12 | **Audit Logging Gap** | `audit_log_service.py` is 1.1KB — likely only logs some events. Write operations without audit trails violate GDPR intent. | ❌ **Not mitigated** — Needs expansion before production. |
| R-13 | **SciBERT Too Large for Free Tier** | SciBERT disabled by default (`USE_SCIBERT_CLASSIFICATION=false`). If re-enabled, model download (~400MB) will exceed Render free tier memory. | ✅ **Managed** — Keep disabled. Use Hugging Face Spaces for SciBERT if needed. |
| R-14 | **Stripe Integration Untested** | `v1/billing.py` exists (3.8KB) but Stripe webhook flow has not been tested with Stripe CLI. | ❌ **Not mitigated** — Must test with `stripe listen --forward-to` before launch. |
| R-15 | **No Analytics** | No PostHog/Mixpanel integration. Operating blind on user behavior and funnel performance. | ❌ **Not mitigated** — Integrate free-tier PostHog before launch for basic funnel tracking. |

---

## 🟢 Green — Low Impact / Managed

| # | Risk | Details | Status |
|---|------|---------|--------|
| R-16 | **ChromaDB Memory Limits** | ChromaDB in-process mode may hit 512MB limit with large RAG stores. | ✅ **Managed** — Use persistent storage mode; fallback to FAISS for dev. |
| R-17 | **CORS Misconfiguration** | CORS not strictly limited to production domains in current config. | ✅ **Managed** — Whitelist Vercel + custom domain in `security_headers.py` before deploy. |
| R-18 | **Supabase Row Limits** | Free tier: 50K rows. High usage without cleanup can hit limits. | ✅ **Managed** — `cleanup.py` exists (2.3KB); verify lifespan wiring. |
| R-19 | **LaTeX Export Stub** | `latex_exporter.py` is 743B — placeholder only. LaTeX downloads will fail. | ✅ **Known** — Marked as ❌ in features, not advertised to users yet. |
| R-20 | **`api.synthesis.js` Was Empty** | Was 36 bytes (empty stub). Has since been implemented via synthesis hooks. | ✅ **Resolved** |

---

## Risk Summary

| Category | Count | Resolved | In Progress | Open |
|----------|-------|---------|------------|------|
| 🔴 Red | 7 | 2 | 2 | 3 |
| 🟡 Yellow | 8 | 1 | 3 | 4 |
| 🟢 Green | 5 | 5 | 0 | 0 |
| **Total** | **20** | **8** | **5** | **7** |

> **7 open risks require action before production launch.** Priority order: R-04 (staging) → R-06 (RBAC) → R-12 (audit log) → R-07 (monitoring) → R-14 (Stripe) → R-05 (E2E tests) → R-15 (analytics).
