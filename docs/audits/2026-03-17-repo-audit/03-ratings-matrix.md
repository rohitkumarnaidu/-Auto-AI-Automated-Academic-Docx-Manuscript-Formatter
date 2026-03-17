# Ratings Matrix

## System Lens Scores

| Lens | Score / 10 | Confidence | Why |
| --- | --- | --- | --- |
| User experience | 6 | Medium | Broad route coverage and polished components exist, but trust is reduced by unstable build/test state and unverified complex flows. |
| UI quality | 7 | Medium | Strong visual effort, rich editor, live preview, quality panels, and varied states are present. Visual consistency still needs tightening. |
| Accessibility | 6 | Low-Medium | There are dedicated accessibility E2E tests and some focus-management work, but local verification is blocked and not all patterns are proven. |
| Backend architecture | 7 | Medium | FastAPI structure, routers, services, migrations, and middleware are substantial. Operational trust is limited by broken local test collection. |
| Frontend architecture | 6 | Medium | The app-router structure, contexts, hooks, and service layer are broad, but build integrity issues lower confidence. |
| AI/ML product readiness | 5 | Medium | The scaffolding is ambitious and substantial, but SciBERT, multi-doc synthesis, and agent flows are not locally proven. |
| Code quality / abstraction | 6 | Medium | Good separation exists in many areas, but there is still drift, TODO spillover, and some suspicious wiring in preview/export flows. |
| Testing / QA | 3 | High | Backend collection is broken and frontend base unit-test setup is broken. Current test inventory is larger than trustable coverage. |
| Security / compliance | 6 | Medium | The scaffold is better than the old plans claim, but validation against live services is missing and docs are inconsistent. |
| Performance / observability | 6 | Low-Medium | Metrics, dashboards, rate limits, and preview optimizations exist in code, but SLO compliance is not locally demonstrated. |
| Deployment / DevOps | 5 | Medium | Workflows, runbooks, and deployment thinking exist, but stale docs plus red build/test state block clean deploy confidence. |
| Product / manager clarity | 4 | High | The codebase and documents tell conflicting stories about what is done and what is missing. |
| Developer experience | 4 | High | Local setup is misleading right now because docs, env names, runtime version, and tests are out of sync. |
| Data / database readiness | 6 | Medium | Schema and migration coverage are meaningful, but database-backed flows were not locally exercised in this audit. |

## Perspective-Specific Ratings

| Perspective | Score / 10 | Strengths | Top Blockers | Next Focus |
| --- | --- | --- | --- | --- |
| User | 6 | Good route breadth, modern editing surfaces, results/download flows | trust, broken edge paths, some feature inconsistency | stabilize critical happy paths |
| Developer | 4 | rich code surface, decent modularization, lots of reusable pieces | env drift, stale docs, broken tests/build | restore local truth and fast feedback loops |
| AI engineer | 5 | Groq/NVIDIA/Ollama paths, RAG scaffolding, agent and synthesizer code | limited runtime proof, disabled/weak SciBERT confidence | benchmark and fixture-driven validation |
| Tester / QA | 3 | many test files already exist | collection/build failures make the suite untrustworthy | fix base test harnesses first |
| Manager / product owner | 4 | there is more product built than expected | plans and docs badly misstate reality | rebuild roadmap from current repo truth |
| DevOps / deployment owner | 5 | workflows, runbooks, metrics, deployment intent | docs stale, no reliable green baseline, service-heavy topology | produce a deployable minimum architecture |
| Security reviewer | 6 | CSP, JWKS, rate limiting, audit logging service, signed URLs, security workflow | live validation missing, some docs outdated | verify controls in controlled integration runs |

## Module Rollup

| Module | Status | Score / 10 | Summary |
| --- | --- | --- | --- |
| Formatter Mode A | Completed but needs improvement | 7 | Core formatter UX is broad and real, but export consistency and end-to-end proof still lag. |
| Formatter Mode B | Partially completed | 6 | Live preview exists beyond plan expectations, but production hardening and contract alignment remain open. |
| Generator Mode A | Partially completed | 5 | Synthesis surface exists, but external dependency and runtime proof gaps are still significant. |
| Generator Mode B | Partially completed | 5 | Agent UI and backend are materially implemented, but need acceptance-proof and stability work. |
| Security / Billing | Completed but needs improvement | 6 | Strong scaffolding, limited local proof. |
| CI/CD / Observability | Completed but needs improvement | 5 | Files exist, but repo state would not currently clear the gates cleanly. |
| Documentation | Not completed | 3 | Important docs exist, but top-level truthfulness is poor. |
