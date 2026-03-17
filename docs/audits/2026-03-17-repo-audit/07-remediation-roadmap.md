# Remediation Roadmap

## Phase 0: Restore Truth And Fast Feedback
Goal: get to a trustworthy local baseline before any new feature work.

1. Rebuild backend local environment on Python 3.12.
2. Fix backend pytest collection by resolving repo-package import behavior.
3. Repair the `nougat/albumentations` validation crash path after import resolution is correct.
4. Fix frontend `generate-tests.js` so `npm run build` passes.
5. Add the missing frontend unit-test dependency and restore a small green Vitest subset.
6. Freeze a short `known-good local commands` section in docs.

Exit criteria:
- backend collection works
- frontend build works
- frontend unit test harness works
- local setup instructions are truthful

## Phase 1: Canonical Documentation Reset
Goal: stop the docs from fighting the codebase.

1. Rewrite root README and backend README.
2. Replace Vite-era env names and 5173 references with current Next.js truth.
3. Publish canonical architecture, API, deployment, and testing docs.
4. Mark stale/generated docs as deprecated or migrate their content into canonical docs.

Exit criteria:
- a new contributor can bootstrap the repo without being misled
- architecture docs no longer claim missing or obsolete layers as current truth

## Phase 2: Contract And Smoke Validation
Goal: prove the highest-value flows with minimal deterministic coverage.

1. Add backend contract smoke tests for:
  - `/api/v1/templates`
  - document status/download contract
  - preview live endpoint
  - generator session create/get/update
2. Add frontend/browser smoke tests for:
  - `/edit`
  - `/results`
  - `/live`
  - `/generator/agent`
3. Add one deprecation-header test for legacy routes.
4. Add one signed-download test and one virus-scan-path test under service-aware profile.

Exit criteria:
- every major product mode has at least one trusted happy-path smoke
- legacy and v1 contracts are both proven where still supported

## Phase 3: Product Hardening
Goal: remove contract drift and partial exposure in existing features.

1. Unify template source of truth between frontend and backend.
2. Decide TEX support contract now:
  - fully supported and tested
  - or fully hidden until complete
3. Harden live preview export path and websocket reconnect flow.
4. Verify template-editor create/update/list behavior end-to-end.
5. Validate generator multi-doc and agent flows against deterministic fixtures.

Exit criteria:
- formatter and generator surfaces no longer rely on optimistic assumptions
- preview/export/template behavior is consistent across UI and backend

## Phase 4: Service-Backed Validation
Goal: validate the code against the real supporting services.

1. Run controlled integration checks with Redis, GROBID, Docling, ClamAV, Supabase, and Stripe test mode.
2. Verify audit logs, signed URLs, billing webhooks, and retention jobs.
3. Run targeted latency checks for preview and formatter flows.
4. Promote passing smokes into CI-protected workflows.

Exit criteria:
- core service-backed flows are proven
- CI gates represent meaningful protection rather than just file presence

## Phase 5: Launch Readiness
Goal: turn the current codebase into a deployable, supportable product.

1. Select the minimum production architecture.
2. Lock the deployment topology and environment contract.
3. Run rollback and incident-response drills using the existing runbook structure.
4. Establish one product dashboard and one release checklist.

Exit criteria:
- green build and trusted smoke suite
- truthful docs
- deployment path that matches the actual workload profile
