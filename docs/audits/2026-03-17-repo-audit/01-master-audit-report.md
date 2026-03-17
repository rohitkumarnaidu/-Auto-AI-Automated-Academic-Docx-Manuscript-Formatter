# Master Audit Report

## Overall Verdict
ScholarForm AI is no longer a 25 percent-complete prototype. The current repo contains a substantial amount of the architecture and feature surface that the planning docs describe. The real problem is different: the codebase has moved ahead of the documents, while local test/build integrity has fallen behind. As of this audit, the system is best described as `feature-rich but operationally unstable`.

## Audit Method
- Repo reality first: code, config, tests, workflows, routes, migrations, docs.
- Plan comparison second: four external markdown planning files plus the master `.docx`.
- Status labels used:
  - `Completed`
  - `Completed but needs improvement`
  - `Partially completed`
  - `Not completed`
  - `Obsolete / incorrect requirement`

## Normalized Requirement Ledger

### Runtime, Contracts, And Platform
| Source | Requirement | Repo Evidence | Runtime Evidence | Status | Risk | Notes | Recommended Action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `agent_prompts_part1`, `implementation_plan`, master plan | Pin backend runtime to Python 3.12 | `backend/pyproject.toml`, `backend/docker/Dockerfile`, `backend/mypy.ini`, `.github/workflows/backend-ci.yml` all point to 3.12 | Local virtualenv is 3.11.9 | Completed but needs improvement | High | Repo contract is correct; local execution path is not. | Rebuild local backend env on 3.12 and enforce via bootstrap docs + CI. |
| planning docs, master plan | Versioned `/api/v1/*` surface | `backend/app/routers/v1/*`, `backend/app/main.py`, legacy successor maps in routers | Not end-to-end exercised locally | Completed but needs improvement | Medium | v1 exists, but docs and runtime proof are inconsistent. | Add contract smoke tests once backend collection works. |
| planning docs | 17 public templates | `backend/app/schemas/document.py`, `backend/app/routers/templates.py` | Not hit via local HTTP due test instability | Completed | Low | Template enum + whitelist are already aligned. | Add one direct API smoke in future CI. |
| planning docs | Legacy API deprecation behavior | deprecation routing classes and successor maps exist | Not runtime verified | Completed but needs improvement | Medium | Good compatibility intent; needs smoke coverage. | Add deprecation header tests. |

### Formatter Mode A
| Source | Requirement | Repo Evidence | Runtime Evidence | Status | Risk | Notes | Recommended Action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Module 0 docs | Upload virus scan before processing | `backend/app/utils/virus_scanner.py`, calls in `backend/app/routers/documents.py` | No ClamAV runtime test in this audit | Completed but needs improvement | Medium | Implementation exists; live antivirus path not validated. | Add EICAR smoke test in service-aware integration profile. |
| Module 2 docs | Rich `/edit` page with TipTap | `frontend/app/(formatter)/edit/page.jsx` | Not browser-verified in this audit | Completed | Low | Planning docs claiming textarea-only state are stale. | Keep; add focused Playwright test to trusted subset. |
| Module 2 docs | Quality analysis panel on results page | `frontend/app/(formatter)/results/page.jsx` | Static inspection only | Completed | Low | Panel is implemented and wired for backend quality fields. | Ensure backend always returns stable schema. |
| Module 2 docs | Download page limited to working formats until LaTeX is ready | `frontend/app/(formatter)/download/page.jsx`, `frontend/src/services/api.documents.js` | Static inspection only | Partially completed | Medium | UI mostly gates TEX, but a TEX bypass helper still exists and TODO remains. | Normalize supported formats in one source of truth. |
| planning docs | Template editor save to API | `frontend/app/(formatter)/(protected)/template-editor/page.jsx`, `frontend/src/services/api.templates.js`, `backend/app/routers/templates.py` | Static inspection only | Completed but needs improvement | Medium | Create + list path exist; UX falls back to local storage on failure and update flow is not strongly audited. | Add explicit create/update/delete contract tests. |
| planning docs | Batch upload end-to-end | route + components exist | No trustworthy runtime proof | Partially completed | Medium | Surface exists, but acceptance is not validated here. | Add stable happy-path smoke after backend and build fixes. |
| master plan | LaTeX export | TEX-specific helpers and feature flag references exist | Local verification absent | Partially completed | Medium | Support is inconsistent across backend/frontend/docs. | Freeze one contract: either supported now with tests or hidden entirely. |

### Formatter Mode B (Live Preview)
| Source | Requirement | Repo Evidence | Runtime Evidence | Status | Risk | Notes | Recommended Action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Module 3 docs, master plan | `/api/v1/preview/live` endpoint | `backend/app/routers/preview.py` | Not exercised end-to-end | Completed but needs improvement | Medium | HTML preview path exists. | Add latency + schema smoke test. |
| Module 3 docs, master plan | WebSocket preview endpoint | `backend/app/routers/preview.py` websocket handler | Not exercised | Completed but needs improvement | Medium | WS path exists with heartbeat and pubsub. | Add one Playwright or pytest websocket smoke after environment repair. |
| Module 3 docs | `/live` split-screen editor page | `frontend/app/(formatter)/live/page.jsx`, split editor components/hooks | Not browser-verified | Partially completed | High | Feature exists, but export wiring appears suspicious and template inventory is hardcoded. | Align live export route with backend contract and source template list from API. |
| master plan | No-LLM hot path during typing | `useLivePreviewSocket` + backend preview renderer structure imply HTML-only flow | Not formally proven | Completed but needs improvement | Medium | Architecture intent matches the plan. | Add a guard/test that AI is only user-triggered. |

### Generator Mode A (Multi-Doc Synthesis)
| Source | Requirement | Repo Evidence | Runtime Evidence | Status | Risk | Notes | Recommended Action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Module 4 docs, master plan | Session persistence tables and service | generator migration + `GeneratorSessionService` | DB not exercised locally | Completed but needs improvement | Medium | Persistence layer exists. | Add DB-backed smoke after environment repair. |
| Module 4 docs | Multi-doc synthesizer pipeline | `backend/app/pipeline/synthesis/synthesizer.py` | No end-to-end proof | Partially completed | High | Core class exists, but full happy path depends on external services and stable tests. | Build one deterministic fixture-based synthesis smoke path. |
| Module 4 docs | Multi-upload synthesis UI | `frontend/app/(generator)/(protected)/multi-upload/page.jsx` and generator components | Not browser-verified | Partially completed | Medium | Substantial UI surface exists. | Add upload-state and export-flow proof after build fix. |
| master plan | RAG-backed session Q&A | vector store + session routes/components exist | Not runtime verified | Partially completed | Medium | Architecture is present; local proof missing. | Add non-LLM fixture-mode tests around retrieval behavior. |

### Generator Mode B (AI Agent)
| Source | Requirement | Repo Evidence | Runtime Evidence | Status | Risk | Notes | Recommended Action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Module 5 docs | Task parser | `backend/app/pipeline/generation/task_parser.py` | Not runtime verified | Completed but needs improvement | Medium | Real parser exists. | Add schema and failure-mode unit tests. |
| Module 5 docs | Outline approval backend | `backend/app/routers/v1/generator.py` + agent pipeline resume flow | Not exercised locally | Completed but needs improvement | Medium | Endpoint exists; acceptance not proven. | Add contract tests once backend collection is fixed. |
| Module 5 docs | Agent page with outline, chat, document pane | `frontend/app/(generator)/(protected)/agent/page.jsx`, generator components | Static only | Completed but needs improvement | Medium | UI is materially ahead of plan docs. | Validate with targeted browser smoke after build repair. |
| master plan | Section rewrite and iterative refinement | rewrite flow exists in `backend/app/pipeline/generation/agent.py` and frontend detection logic | Not runtime verified | Partially completed | Medium | Code exists, but trust is limited. | Add deterministic section-rewrite test. |
| planning docs | Export + session save for agent | document save/versioning exists; LaTeX/export maturity inconsistent | No local proof | Partially completed | Medium | Saved-session scaffolding exists, but export maturity is uneven. | Stabilize export contract across agent/synthesis/formatter. |

### AI / ML / Security / Billing / DevOps
| Source | Requirement | Repo Evidence | Runtime Evidence | Status | Risk | Notes | Recommended Action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Module 6 docs | Groq tier in LLM fallback | `backend/app/services/llm_service.py`, settings fields in config and `.env.example` | Not live-verified | Completed but needs improvement | Medium | Planning docs claiming NVIDIA + Ollama only are stale. | Add provider-order unit tests and env docs. |
| Module 6 docs | SciBERT feature flag and benchmark path | settings flag, tests, classifier code | Not benchmarked locally | Partially completed | Medium | The path exists but is still operationally weak/disabled by default. | Separate correctness work from runtime-hardening work. |
| Module 7 docs | JWKS token verification | `backend/app/security/jwks_verifier.py` | Not live-verified | Completed but needs improvement | Medium | Real verifier exists. | Add fixture-based JWT contract tests in stable suite. |
| Module 7 docs | Audit logging | service + migration exist | Not DB-verified | Completed but needs improvement | Medium | Real implementation exists; no local DB proof. | Add write-operation audit assertions. |
| Module 7 docs | Billing and plan gating | backend billing router, frontend settings billing tab, `planTier.js` | Not live-verified | Completed but needs improvement | Medium | Surface exists, but Stripe path is not locally proven. | Keep behind explicit feature/config checks. |
| Module 8 docs | CI workflows | `.github/workflows/*.yml` exist | Current repo state would not pass all checks | Completed but needs improvement | High | Docs claiming CI absence are stale; CI value is reduced by current repo failures. | Fix local build/test blockers first. |
| Module 8 docs | Runbooks and ADRs | `docs/runbooks/*`, `docs/adr/*` | N/A | Completed | Low | This area is better than plans imply. | Preserve and fold into canonical docs set. |

### Documentation Truthfulness
| Source | Requirement | Repo Evidence | Runtime Evidence | Status | Risk | Notes | Recommended Action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| user request | Canonical, industry-level docs set | Existing docs are fragmented and partly stale | N/A | Not completed | High | Root and generated docs still reference Vite-era env names, old ports, and outdated architecture assumptions. | Build a canonical docs set and deprecate stale/generated copies. |
| planning docs | Spring Boot gateway as locked architecture | Repo contains no gateway project and FastAPI owns the platform surface | N/A | Obsolete / incorrect requirement | Medium | This is planning drift, not a missing repo feature. | Treat FastAPI-first as the current architecture until a gateway actually exists. |
| master plan and generated docs | Vite-based frontend envs and port 5173 | Next.js app on 3000; `.env.example` uses `NEXT_PUBLIC_*` | N/A | Obsolete / incorrect requirement | Medium | Current docs would mislead onboarding and deployment. | Rewrite README, deployment guide, and generated docs sources. |

## Major Findings
1. The repo is ahead of the plans in feature breadth, but behind in operational trust.
2. The biggest immediate blockers are not missing features. They are broken local verification paths and stale documentation.
3. Backend test health is currently the weakest technical signal because collection fails before assertions.
4. Frontend route coverage and UI surface are broad, but the build/test layer is not trustworthy yet.
5. The docs layer is now a liability: it actively misstates architecture, env vars, local ports, and completion status.

## Top Priorities
1. Repair backend test collection and Python 3.12 local runtime parity.
2. Repair frontend build and unit test base dependencies.
3. Freeze one truthful architecture and deployment story in docs.
4. Re-run a targeted smoke matrix for formatter, live preview, multi-doc synthesis, and agent flows.
5. Only then use the audit outputs to plan deeper product hardening.
