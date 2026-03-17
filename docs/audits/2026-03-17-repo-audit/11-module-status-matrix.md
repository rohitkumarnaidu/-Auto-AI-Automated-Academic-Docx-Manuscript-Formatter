# Module Status Matrix

## Backend Modules

| Module | Status | Key Files | What Is Done | What Is Partial / Missing | Focus |
| --- | --- | --- | --- | --- | --- |
| Documents / upload / download | Completed but needs improvement | `backend/app/routers/documents.py`, `backend/app/services/document_service.py`, `backend/app/utils/virus_scanner.py` | upload pipeline, virus scan hook, signed download flow, delete flow exist | service-backed proof is still missing; test suite is blocked | restore backend tests, then add document smoke coverage |
| Templates | Completed | `backend/app/routers/templates.py`, `backend/app/schemas/document.py` | 17-template enum/whitelist is present; custom template CRUD exists | needs runtime contract proof | add one trusted template API smoke |
| Preview / realtime | Completed but needs improvement | `backend/app/routers/preview.py`, `backend/app/services/preview_renderer.py`, `backend/app/realtime/*` | live preview endpoint, websocket flow, SSE AI suggestion path exist | latency/reconnect/export contract not proven locally | validate preview happy path |
| Generator sessions | Completed but needs improvement | `backend/app/services/generator_session_service.py`, `backend/alembic/versions/20260311_0001_generator_tables.py` | DB-backed session/message/document persistence exists | DB-backed runtime proof missing | add fixture-backed CRUD tests |
| Multi-doc synthesis | Partially completed | `backend/app/pipeline/synthesis/synthesizer.py`, `backend/app/routers/v1/synthesis.py` | synthesizer pipeline and session event model exist | end-to-end proof and fixture confidence are weak | prove one deterministic 2-doc fixture flow |
| Agent generator | Partially completed | `backend/app/pipeline/generation/task_parser.py`, `agent.py`, `section_prompts.py`, `quality_scorer.py` | parser, outline flow, section writing, rewrite flow, quality scoring exist | acceptance proof and full export maturity lag | validate prompt -> outline -> approve -> write -> export |
| Security / auth | Completed but needs improvement | `backend/app/security/jwks_verifier.py`, `backend/app/middleware/*`, `backend/app/services/audit_log_service.py` | JWKS, rate limiting, CSP/security headers, audit log service, abuse/tier logic exist | live validation and auth test trust missing | add fixture JWT and policy tests |
| Billing | Completed but needs improvement | `backend/app/routers/v1/billing.py`, migrations/models | billing endpoints and plan-tier data path exist | live Stripe proof absent | keep behind config, test in Stripe sandbox later |
| Observability / DevOps | Completed but needs improvement | `.github/workflows/*`, `backend/app/routers/metrics.py`, `ops/*`, `docs/runbooks/*` | workflows, metrics, dashboards, runbooks exist | repo is not green enough for trustable gating | fix local baseline first |

## Frontend Modules

| Module | Status | Key Files | What Is Done | What Is Partial / Missing | Focus |
| --- | --- | --- | --- | --- | --- |
| Shared app shell / auth / theme | Completed but needs improvement | `frontend/components/ClientProviders.jsx`, `frontend/src/context/*`, `components/header/ThemeToggle.jsx` | auth, theme, providers, route guards exist | needs trusted tests after harness repair | rerun focused auth/theme tests |
| Formatter upload / processing / results | Completed but needs improvement | `frontend/app/(formatter)/upload/page.jsx`, `processing/page.jsx`, `results/page.jsx` | formatter core route surface is present and polished | build/test instability reduces trust | verify route build and one browser smoke |
| Formatter edit | Completed | `frontend/app/(formatter)/edit/page.jsx` | TipTap editor already implemented | needs smoke proof only | keep, do not rewrite |
| Formatter live preview | Partially completed | `frontend/app/(formatter)/live/page.jsx`, `src/components/live-preview/*`, `src/hooks/useLivePreviewSocket.js` | split editor, websocket usage, AI sidebar exist | export path and hardcoded template list need hardening | align with backend contract |
| Download / export | Partially completed | `frontend/app/(formatter)/download/page.jsx`, `src/services/api.documents.js` | working DOCX/PDF path is mostly represented | TEX support is inconsistent; TODO remains | freeze supported formats |
| Template editor | Completed but needs improvement | `frontend/app/(formatter)/(protected)/template-editor/page.jsx`, `src/services/api.templates.js` | cloud/local save path exists | CRUD proof and UX fallback clarity need work | add template save/update smoke |
| Batch upload | Partially completed | `frontend/app/(formatter)/(protected)/batch-upload/page.jsx`, `src/components/BatchUploadPanel.jsx` | route and component surface exist | end-to-end proof missing | validate one happy path after backend fix |
| Generator multi-upload | Partially completed | `frontend/app/(generator)/(protected)/multi-upload/page.jsx`, generator components | rich multi-doc surface exists | backend proof and export reliability need validation | test 2-doc happy path |
| Generator agent | Completed but needs improvement | `frontend/app/(generator)/(protected)/agent/page.jsx`, `src/components/generator/*` | outline pane, chat pane, document build pane, session history exist | still needs end-to-end proof | validate core agent flow |
| Settings / billing / admin / profile | Completed but needs improvement | `frontend/app/(shared)/(protected)/*` | substantial shared-account surface exists | build/test trust is lower than route breadth | verify highest-risk pages only |

## Docs And Delivery Modules

| Module | Status | Key Files | What Is Done | What Is Partial / Missing | Focus |
| --- | --- | --- | --- | --- | --- |
| README / setup docs | Not completed | `README.md`, `backend/README.md` | docs exist | they are stale and misleading | rewrite |
| Architecture / API docs | Partially completed | `docs/architecture.md`, `docs/api_reference.md`, ADRs | useful material exists | top-level docs are stale; ADRs are better than summaries | rebuild canonical set |
| Deployment / runbooks | Completed but needs improvement | `docs/deployment_guide.md`, `docs/runbooks/*` | runbooks are useful | deployment guide is stale | merge into canonical deployment doc |
