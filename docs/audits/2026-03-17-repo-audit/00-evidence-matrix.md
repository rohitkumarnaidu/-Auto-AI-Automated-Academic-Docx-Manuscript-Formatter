# Evidence Matrix

## Local Validation Commands

| Area | Command | Outcome | Classification | Notes |
| --- | --- | --- | --- | --- |
| Backend runtime | `python --version` via repo virtualenv | `Python 3.11.9` | Fail | Backend contract requires Python `>=3.12,<3.13`. Repo config is pinned, local environment is not. |
| Backend test collection | `pytest --collect-only -q` | Import error before collection | Fail | `tests/conftest.py` imports `app.models`, but local resolution lands in a third-party installed `app` package and crashes in `nougat/albumentations`. |
| Backend unit-ish suite | `pytest tests -m "not integration and not llm" -x -q` | Same pre-collection failure | Fail | The suite is blocked before any marker filtering helps. |
| Frontend unit tests | `npm test` | 5 failed suites / 3 passed files | Fail | Failing suites error on missing `@testing-library/dom`; API service tests pass. |
| Frontend production build | `npm run build` | Type error in `frontend/generate-tests.js` | Fail | Build currently blocked by repo defect, not by external services. |
| Backend static config check | direct file inspection | Python 3.12 pin, Dockerfile, CI config present | Pass | Repo configuration is aligned; local environment is not. |
| Frontend route surface check | direct file inspection | 34 page routes found | Pass | Route inventory is materially broader than the planning docs imply. |
| Frontend Playwright surface check | direct file inspection | 93 E2E spec files found | Pass | Test count exists on disk, but trust is low until build and base test setup are fixed. |

## Representative Repo Evidence

### Backend
- Python contract is pinned in:
  - `backend/pyproject.toml`
  - `backend/docker/Dockerfile`
  - `.github/workflows/backend-ci.yml`
- v1 API and legacy compatibility exist through:
  - `backend/app/main.py`
  - `backend/app/routers/v1/`
  - legacy routers under `backend/app/routers/`
- Security/compliance scaffolding exists in:
  - `backend/app/utils/virus_scanner.py`
  - `backend/app/security/jwks_verifier.py`
  - `backend/app/services/audit_log_service.py`
  - `backend/app/services/document_service.py`
  - `backend/app/middleware/security_headers.py`
  - `backend/app/middleware/tier_rate_limit.py`
- Generator persistence and document versioning exist in:
  - `backend/app/services/generator_session_service.py`
  - `backend/alembic/versions/20260311_0001_generator_tables.py`
  - `backend/app/pipeline/generation/agent.py`
  - `backend/app/pipeline/synthesis/synthesizer.py`

### Frontend
- Theme is centralized in:
  - `frontend/src/context/ThemeContext.jsx`
  - `frontend/components/header/ThemeToggle.jsx`
- Rich editor and live preview exist in:
  - `frontend/app/(formatter)/edit/page.jsx`
  - `frontend/app/(formatter)/live/page.jsx`
  - `frontend/src/components/live-preview/SplitEditor.jsx`
  - `frontend/src/hooks/useLivePreviewSocket.js`
- Generator and agent UI exist in:
  - `frontend/app/(generator)/(protected)/multi-upload/page.jsx`
  - `frontend/app/(generator)/(protected)/agent/page.jsx`
  - `frontend/src/components/generator/`
- Current frontend defects are directly evidenced in:
  - `frontend/generate-tests.js`
  - `frontend/package.json`
  - failing `npm test` output for missing `@testing-library/dom`

## Validation Limits
- No live Supabase, Redis, GROBID, Docling, ClamAV, Stripe, or Render verification was assumed.
- Any item marked implemented but unverified should still be treated as needing a targeted smoke test after the repo is stabilized.
