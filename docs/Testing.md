# Testing Strategy

> **Last Updated:** June 2026  
> **Current State:** Backend coverage at ~21% (up from ~5%). Deep test suite (854+ tests) covers all core pipeline modules. Frontend uses vitest + Playwright E2E.

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
cd backend
pytest tests -m "not integration and not llm" -x -q
```

**Deep tests for a specific module:**
```bash
pytest tests/test_rag_engine_deep.py -v --tb=short -o "addopts="
```

**Full suite (all services running):**
```bash
cd backend && pytest
```

**Lint and type-check:**
```bash
cd backend
ruff check app --config ruff.toml
mypy --config-file mypy.ini app
```

### Current Blocker Status

| Blocker | Status |
|---------|--------|
| Python 3.12 import collision | ✅ Resolved — CI runs 3.12.x |
| asyncio mode | ✅ `asyncio_mode = auto` set in `pytest.ini` |
| Missing env vars at collection | ✅ Service-dependent tests have proper markers |

### Deep Test Coverage (June 2026)

Enterprise-grade deep test files with intensive mocking, targeting >80% per-module coverage:

| Module | File | Tests | Coverage |
|--------|------|-------|----------|
| DocxParser | `test_docx_parser_deep.py` | 108 | ~90% |
| PipelineOrchestrator | `test_pipeline_orchestrator_deep.py` | 49 | ~82% |
| Formatter | `test_formatter_deep.py` | 207 | ~88% |
| Classifier | `tests/classifier/test_classifier_deep.py` | 92 | ~86% |
| DocumentService | `test_document_service_deep.py` | 110 | 86% |
| ReasoningEngine | `test_reasoning_engine_deep.py` | 87 | 80% |
| AgentPipeline | `test_agent_deep.py` | 120 | ~84% |
| PdfParser | `test_pdf_parser_deep.py` | 71 | 88% |
| RagEngine | `test_rag_engine_deep.py` | 87 | 91% |
| **Total** | | **931** | |

**Regression health:** `854/854` passed (all non-integration, non-llm tests).

---

## 2. Frontend Profiles (`vitest` + Playwright)

### Prerequisites

```bash
# @testing-library/dom is REQUIRED — common missing-dep failure
npm install @testing-library/dom --save-dev
```

### Vitest (Unit / Component Tests)

```bash
cd frontend
npm test
# or
npx vitest
```

**What it tests:** React hooks (`useLivePreviewSocket`, `useGeneratorSessionStream`), context providers, isolated page components.

### Playwright (E2E Smoke Tests)

```bash
cd frontend
# Requires running backend
npm run test:e2e           # headless
npm run test:e2e:headed    # headed
```

---

## 3. Critical Test Paths (Priority Order)

| # | Flow | Test File |
|---|------|----------|
| 1 | Guest upload → process → download | `frontend/e2e/upload-journey.spec.js` |
| 2 | Auth: signup → login → dashboard | `frontend/e2e/auth-flow.spec.js` |
| 3 | Template selection → DOCX export | `frontend/e2e/formatter-upload.spec.js` |
| 4 | Live preview WebSocket connects | `frontend/e2e/formatter-live-preview.spec.js` |
| 5 | Agent chat → outline → approve | `frontend/e2e/generator-outline-approve.spec.js` |
| 6 | Multi-doc synthesis SSE stream | `frontend/e2e/generator-synthesis.spec.js` |

---

## 4. Test Infrastructure

| Tool | Config |
|------|--------|
| pytest | `pytest.ini` — `asyncio_mode = auto`, coverage fail-under=70 |
| vitest | `vitest.config.js` in frontend root |
| Playwright | `playwright.config.js` in frontend root |
| CI (backend) | `backend-ci.yml` — ruff → mypy → pytest |
| CI (frontend) | `frontend-ci.yml` — eslint → vitest → build → Playwright |

### Key Techniques

- **Two-tier test approach:** Extend existing test files for new features, add `_deep.py` companion files with intensive mocking for full internal method coverage
- **Subdirectory conftest isolation:** Slow parent-level fixtures (e.g., importing `app.main` triggers 18s FastAPI startup) are overridden in subdirectory `conftest.py` files (e.g., `tests/classifier/conftest.py`)
- **Lazy imports:** Modules with circular dependency chains (e.g., `AgentPipeline`) are imported inside fixtures, not at module level
- **Python 3.14 compatibility:** Tests use `unittest.mock.patch` and `pytest` — no `async` decorator needed thanks to `asyncio_mode = auto`

---

## 5. Next Steps

1. Write deep tests for **nougat_parser.py** (0% coverage)
2. Write deep tests for **exporter.py**, **synthesizer.py**, **document_generator.py**
3. Raise project-wide coverage toward 50%
4. Fill E2E critical path stubs with real DOM assertions
