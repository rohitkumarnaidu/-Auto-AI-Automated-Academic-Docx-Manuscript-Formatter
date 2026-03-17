# Documentation Backlog Spec

## Canonical Docs Set To Create Or Rewrite
- `docs/PRD.md`
- `docs/Features.md`
- `docs/UIUX.md`
- `docs/TechStack.md`
- `docs/Database.md`
- `docs/API.md`
- `docs/Architecture.md`
- `docs/Security.md`
- `docs/Deployment.md`
- `docs/AI_Instructions.md`
- `docs/Agent.md`
- `docs/Testing.md`
- `docs/Risk_Register.md`
- `docs/Roadmap.md`

## Source Mapping

| Current File | Decision | Target Canonical Doc | Reason |
| --- | --- | --- | --- |
| `README.md` | Rewrite | root README + `docs/TechStack.md` + `docs/Deployment.md` | Currently stale on env names, ports, and frontend stack. |
| `backend/README.md` | Rewrite | `docs/API.md`, `docs/Architecture.md`, `docs/Testing.md` | Describes an older system shape and older limitations. |
| `docs/api_reference.md` | Rewrite and merge | `docs/API.md` | Useful seed, but stale on route versioning and format support. |
| `docs/architecture.md` | Rewrite | `docs/Architecture.md` | Still claims Vite and in-memory SSE backbone. |
| `docs/deployment_guide.md` | Rewrite | `docs/Deployment.md` | Contains stale ports and old frontend assumptions. |
| `docs/user_guide.md` | Keep and adapt | `docs/Features.md` or product-facing user guide | Can be kept once aligned to current UI. |
| `docs/template_creation.md` | Keep and adapt | `docs/Features.md` + template appendix | Narrow but still useful. |
| `docs/troubleshooting.md` | Keep and adapt | `docs/Testing.md` + `docs/Deployment.md` appendix | Should be updated to current env/runtime truth. |
| `docs/Company_Documentation_FRS_SRS.md` | Replace / mine content | `docs/PRD.md`, `docs/Architecture.md`, `docs/Features.md` | Large source document, but not a clean canonical reference. |
| `docs/adr/*` | Keep | `docs/Architecture.md` references + ADR directory | Strong asset; should remain authoritative for decisions. |
| `docs/runbooks/*` | Keep | `docs/Deployment.md` and operations references | Good operational artifacts already. |
| generated docs scripts/output | Replace or deprecate | canonical docs set | Current generated content still carries stale assumptions. |

## Recommended Creation Order
1. `docs/Architecture.md`
2. `docs/API.md`
3. `docs/Deployment.md`
4. `docs/Testing.md`
5. `docs/TechStack.md`
6. `docs/PRD.md`
7. `docs/Features.md`
8. `docs/Security.md`
9. `docs/Database.md`
10. `docs/UIUX.md`
11. `docs/AI_Instructions.md`
12. `docs/Agent.md`
13. `docs/Risk_Register.md`
14. `docs/Roadmap.md`

## Minimum Content Requirements

### `docs/Architecture.md`
- current production-intended architecture, not aspirational alternatives
- backend/frontend/realtime/background-job topology
- external service dependencies
- decision on gateway vs FastAPI-first current state

### `docs/API.md`
- current v1 routes
- legacy compatibility/deprecation rules
- payload schemas
- auth rules
- known feature flags and partial endpoints

### `docs/Deployment.md`
- supported hosting topologies
- env vars by surface
- local/dev/staging/prod expectations
- worker/background-job considerations

### `docs/Testing.md`
- Python/runtime version contract
- local bootstrap
- unit vs integration vs service-backed profiles
- trusted smoke commands
- known current blockers and how to diagnose them

## Documentation Governance Rules
- One canonical doc per topic.
- Generated docs must not outrank manually curated canonical docs.
- Any roadmap/status claim must cite a repo-validated source or a known owner/date.
- Avoid percentage-complete claims unless tied to a maintained acceptance matrix.
