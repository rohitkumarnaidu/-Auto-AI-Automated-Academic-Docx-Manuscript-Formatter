# Testing Strategy

> **Last Updated:** March 2026 (Codex 5.4 Audit)  
> **Current State:** Test infrastructure exists. Backend has an import collision blocker (Python 3.11.9 → 3.12 fix resolves it). Frontend requires `@testing-library/dom` to be installed.

---

## Overview

The ScholarForm AI testing harness uses segmented profiles to ensure fast feedback for pure logic while enabling comprehensive validation for external services.

---

## 1. Backend Profiles (`pytest` + `pytest.ini`)

### Test Markers

| Marker | Requires | Description |
|--------|---------|-------------|
| `unit` | Nothing | Pure Python logic — no external connections |
| `integration` | Docker (Redis, DB, GROBID) | Needs local infrastructure running |
| `llm` | Live LLM API key | Requires NVIDIA NIM, Groq, or Ollama |
| `service` | Heavy runtime deps | Full stack required |
| `contract` | Running FastAPI | Verifies schema stability across endpoints |

### How to Run

**Fast (no services needed):**
```bash
pytest tests -m "not integration and not llm" -x -q
```

**Full suite (all services running):**
```bash
pytest
```

**Specific test categories:**
```bash
# Only contract tests
pytest tests -m contract

# Integration tests (requires Docker services)
pytest tests -m integration

# Formatter golden files
pytest tests/test_formatter_golden_files.py -v
```

### Current Blockers (Codex-identified)

| Blocker | Cause | Fix |
|---------|-------|-----|
| `INTERNAL ERROR` during collection | Python 3.11.9 import collision with `pytest` module path | Upgrade to Python 3.12.x |
| asyncio mode issue | `asyncio_mode` not set in `pytest.ini` | Add `asyncio_mode = "auto"` to `pyproject.toml` |
| Missing env vars at collection | Redis/ChromaDB/Supabase not mocked | Add `@pytest.mark.integration` skip decorators to service-dependent tests |

### Backend Test Files (46 total)

| Category | Files | Health |
|----------|-------|--------|
| Unit tests | ~20 | ✅ Should pass with no services |
| Integration tests | ~15 | ⚠️ Require Docker services |
| Golden file tests | `test_formatter_golden_files.py` (8.8KB) | ✅ Well-implemented |
| Security tests | `test_jwks_verifier.py`, `test_signed_downloads.py` | ✅ Good |
| SciBERT benchmark | `test_scibert_benchmark.py` (2.9KB) | ⚠️ Needs model to be enabled |

---

## 2. Frontend Profiles (`vitest` + Playwright)

### Prerequisites

```bash
# @testing-library/dom is REQUIRED — common missing-dep failure
npm install @testing-library/dom --save-dev
```

### Vitest (Unit / Component Tests)

Fast testing of React hooks and isolated components using jsdom.

```bash
npm test
# or
npx vitest
```

**What it tests:** React hooks (`useLivePreviewSocket`, `useGeneratorSessionStream`), context providers, isolated page components.

### Playwright (E2E Smoke Tests)

Browser-based testing for happy paths and flows.

```bash
# Individual flows
npx playwright test tests/e2e/upload.spec.js --headed
npx playwright test tests/e2e/results.spec.js --headed
npx playwright test tests/e2e/agent.spec.js --headed
npx playwright test tests/e2e/live.spec.js --headed

# All E2E tests
npx playwright test
```

**E2E Warning:** 93 test files exist but most are stubs (<700 bytes each). Many lack real DOM assertions. The top 20 critical path tests need to be filled in before these are trustworthy.

---

## 3. Critical Test Paths (Priority Order)

The top flows to validate before any deployment:

| # | Flow | Test File |
|---|------|----------|
| 1 | Guest upload → process → download | `tests/e2e/upload.spec.js` |
| 2 | Auth: signup → login → dashboard | `tests/e2e/auth.spec.js` |
| 3 | Template selection → DOCX export | `tests/e2e/results.spec.js` |
| 4 | `/api/v1/health` returns all services OK | `tests/contract/health.spec.js` |
| 5 | `/api/v1/templates` returns 17 templates | `tests/contract/templates.spec.js` |
| 6 | Live preview WebSocket connects | `tests/e2e/live.spec.js` |
| 7 | Agent chat → outline → approve | `tests/e2e/agent.spec.js` |
| 8 | Multi-doc synthesis SSE stream | `tests/e2e/synthesis.spec.js` |

---

## 4. Test Infrastructure

| Tool | Config |
|------|--------|
| pytest | `pyproject.toml` or `pytest.ini` — add `asyncio_mode = "auto"` |
| vitest | `vitest.config.js` in frontend root |
| Playwright | `playwright.config.js` in frontend root |
| CI | `backend-ci.yml` (pytest), `frontend-ci.yml` (vitest + build) |

---

## Current Blockers & Next Steps

1. **Backend:** Resolve Python 3.12 import collision — confirm `python --version` is 3.12.x
2. **Backend:** Add `asyncio_mode = "auto"` to `pyproject.toml`
3. **Frontend:** Install `@testing-library/dom` as dev dependency
4. **E2E:** Fill top 20 critical path stubs with real DOM assertions
5. **Integration:** Verify Docling + GROBID fallback flows across diverse PDF types
6. **Contract:** Run contract tests against running backend to confirm response envelope formats
