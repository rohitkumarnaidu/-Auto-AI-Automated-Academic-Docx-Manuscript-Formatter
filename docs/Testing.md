# Testing Strategy

## Overview
The ScholarForm AI testing harness relies on segmented profiles to ensure fast feedback for pure logic while enabling comprehensive validation for external services. 

## 1. Backend Profiles (`pytest` + `pytest.ini`)

Testing is divided by markers:
- `unit`: Pure logic, no external connection required.
- `integration`: Requires local Docker/infrastructure (Redis, GROBID).
- `llm`: Requires a live LLM (NVIDIA, Ollama).
- `service`: Requires heavy-weight runtime dependencies.
- `contract`: Verifies schema stability across core endpoints.

### How to Run:
**Trusted-Core (Fast Feedback):**
```bash
pytest tests -m "not integration and not llm" -x -q
```
*This command runs safely without any running services.*

**Full Suite:**
```bash
pytest
```

## 2. Frontend Profiles (`vitest` + Playwright)

### Vitest (Unit / Contexts)
Fast testing of React hooks and isolated pages using DOM interactions.
*Note: `@testing-library/dom` is required.*
```bash
npm test
```

### Playwright (E2E Smoke Tests)
Systematic browser-based testing for happy paths.
```bash
npx playwright test tests/e2e/upload.spec.js --headed
npx playwright test tests/e2e/results.spec.js --headed
npx playwright test tests/e2e/agent.spec.js --headed
npx playwright test tests/e2e/live.spec.js --headed
```

## Current Blockers & Next Steps
- Implement frontend E2E stubs with real DOM assertions.
- Verify Docling + GROBID fallback flows across diverse PDFs.
