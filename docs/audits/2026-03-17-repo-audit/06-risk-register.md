# Risk Register

| ID | Risk | Area | Likelihood | Impact | Severity | Current Signal | Mitigation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R1 | Local backend runtime is not Python 3.12 | backend / DX | High | High | Critical | Local env reports Python 3.11.9 | Recreate backend env on 3.12 and document the bootstrap path. |
| R2 | Backend tests do not collect due import/package collision | backend / QA | High | High | Critical | `pytest --collect-only` fails before assertions | Fix import resolution and isolate the repo package from site-packages collision. |
| R3 | `nougat/albumentations` dependency path crashes backend verification | backend / dependencies | High | High | Critical | crash occurs during wrong import chain | Pin/repair dependency graph after fixing import path. |
| R4 | Frontend production build is red | frontend / release | High | High | Critical | `npm run build` fails on `generate-tests.js` | Fix the offending file and add build check to trusted local loop. |
| R5 | Frontend base unit-test harness is broken | frontend / QA | High | High | Critical | missing `@testing-library/dom` | Align test dependencies and rerun minimal suite. |
| R6 | Documentation drift causes wrong engineering decisions | product / docs | High | High | High | stale Spring Boot, Vite, port, and completion claims | Replace stale docs with canonical truth and deprecate generated copies. |
| R7 | Live preview may not be production-safe despite code presence | formatter B | Medium | High | High | feature exists but is not locally proven | Add targeted preview websocket/export smoke tests. |
| R8 | Generator and synthesis flows may fail under real service conditions | generator | Medium | High | High | code exists; no trusted local E2E proof | Build deterministic fixture-mode tests before service-backed tests. |
| R9 | Billing/security controls are scaffolded but not fully validated | security / billing | Medium | High | High | router/service presence without live validation | Add controlled integration runs with test credentials later. |
| R10 | CI files exist but will not provide reliable gating while repo is red | DevOps | High | Medium | High | current local failures would trip workflows | Fix local build/test blockers before expanding workflow complexity. |
| R11 | Hardcoded frontend template lists may drift from backend template truth | frontend / contract | Medium | Medium | Medium | live page contains static template list | Source templates from backend or a shared config. |
| R12 | TEX/LaTeX support is inconsistently exposed | formatter / generator | Medium | Medium | Medium | TODOs and bypass helpers still exist | Either fully support + test TEX or fully hide it until ready. |
| R13 | Multi-service deployment could become fragile if hosted on the wrong platforms | deployment | Medium | High | High | app uses long-running jobs, SSE/WS, external workers, Redis | Use split hosting aligned to workload type. |
| R14 | Playwright test count may give false confidence | QA | High | Medium | Medium | 93 specs exist but build is broken | Restore trusted baseline, then graduate tests into a known-good subset. |
| R15 | Product roadmap remains tied to stale completion percentages | management | High | Medium | Medium | plans still claim 25 percent complete / 75 percent remaining | Rebuild roadmap from the audit package, not old percentages. |

## Most Likely Failure Modes By Stage
- Coding:
  - import/path drift
  - contract mismatches between frontend and backend
  - feature-flag leakage
- Testing:
  - environment mismatch
  - service dependency flakiness
  - failing suites that do not actually reach project code
- Deployment:
  - wrong platform for long-running workers/websockets
  - stale env vars from docs
  - migration/runtime divergence
- Operations:
  - low-confidence alerting because correctness proof is missing
  - partial features exposed before end-to-end proof exists
