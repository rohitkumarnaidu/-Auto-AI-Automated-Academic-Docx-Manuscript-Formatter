# ScholarForm AI Repo Audit Package (2026-03-17)

This folder is the repo-grounded audit package for the current `automated-manuscript-formatter` codebase.

## Scope
- Compared the current repo against:
  - `agent_prompts_part1.md.resolved`
  - `agent_prompts_part2.md.resolved`
  - `implementation_plan_part2.md.resolved`
  - `implementation_plan.md.resolved`
  - `ScholarForm_AI_Complete_Master_Plan_v4_FINAL.docx`
- Audit basis: current repo/runtime is the truth baseline; planning docs are target/reference documents.
- Validation depth: repo + local only. No assumptions about live Supabase, Redis, Stripe, Render, or external hosted services.

## Key Outcome
The repo is materially more complete than the planning documents claim, but it is not release-stable yet because test/build integrity and documentation drift are still significant blockers.

## Files
- `00-evidence-matrix.md`: local command results and validation notes.
- `01-master-audit-report.md`: normalized requirement ledger and overall audit conclusion.
- `02-reality-vs-plan-diff.md`: stale assumptions, obsolete requirements, and document drift.
- `03-ratings-matrix.md`: module scores and perspective-specific ratings.
- `04-backend-audit.md`: backend architecture, testing, security, and deployment analysis.
- `05-frontend-audit.md`: UX, UI, accessibility, build/test, and route analysis.
- `06-risk-register.md`: prioritized risks with mitigations.
- `07-remediation-roadmap.md`: ordered implementation roadmap.
- `08-documentation-backlog-spec.md`: canonical docs backlog and source mapping.
- `09-innovation-and-preemptive-solutions.md`: higher-level solutions, deployment options, and next-gen ideas.
- `10-prompt-coverage-checklist.md`: direct mapping of your original prompt asks to the audit outputs and completion status.
- `11-module-status-matrix.md`: backend/frontend module-by-module status with key files, what is done, what is partial, and what is missing.
- `12-testing-status-summary.md`: explicit answer on whether backend/frontend testing is complete and what blocked it.
- `13-ui-color-and-focus-notes.md`: direct UI color/focus recommendations and whether color changes are needed now.

## Executive Summary
- Completed or largely implemented in code: v1 API surface, preview/live websocket flow, generator session persistence primitives, CI workflows, runbooks, ADRs, theme centralization, TipTap editor, quality score panel, signed downloads, billing/security scaffolding.
- Partially completed or weak: integration-test health, frontend export model, live preview production hardening, multi-doc/generator end-to-end proof, SciBERT readiness, deployment documentation, docs canonicalization.
- Blockers discovered during local validation:
  - Backend local virtualenv is Python `3.11.9`, while backend contract is `>=3.12,<3.13`.
  - Backend pytest fails before collection because local imports resolve into a third-party `app` package and then crash inside `nougat/albumentations`.
  - Frontend Vitest is broken because `@testing-library/dom` is missing.
  - Frontend production build fails on `frontend/generate-tests.js`.
  - Root and generated docs still contain stale Vite-era env names and outdated architecture assumptions.
