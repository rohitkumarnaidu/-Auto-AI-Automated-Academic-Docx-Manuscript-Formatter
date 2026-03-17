# Backend Audit

## Current Strengths
- The backend is not a thin prototype. It has meaningful separation across routers, services, pipeline stages, middleware, models, schemas, and migrations.
- The v1 contract surface exists alongside legacy successor mapping.
- Security and compliance scaffolding are materially present: JWKS verifier, audit logging service, signed download support, rate limiting, CSP/security headers, file cleanup hooks, and virus scanning utility.
- Generator/session persistence is real, not aspirational.
- Observability pieces exist: Prometheus exposure, queue depth updates, metrics routes, dashboards, and runbooks.

## What Is Completed
- Python 3.12 contract in repo config.
- Template enum and 17-template whitelist.
- Groq fallback chain in `llm_service.py`.
- Virus scan utility + router integration.
- Session persistence services and migrations.
- Signed download URL generation and verification.
- Document deletion service path.
- HTTPS redirect/HSTS wiring.
- File cleanup lifecycle hooks.
- Billing router, audit log service, rate limiting, JWKS verification, security workflow, and runbooks.

## What Is Completed But Needs Improvement
- `/api/v1/*` contract stabilization: the surface exists, but acceptance proof is missing.
- Security controls: code is ahead of the plans, but runtime proof is not.
- Generator and synthesis persistence: DB-backed structure exists, but no local DB-backed smoke was run.
- CI-readiness: backend CI workflow exists, but local test collection is currently broken.
- Observability: instrumentation exists, but SLO validation was not executed.

## What Is Partially Completed
- Integration-test stability.
- SciBERT readiness and confidence.
- Multi-doc synthesis happy-path proof.
- Agent workflow acceptance proof.
- External-service validation for ClamAV, GROBID, Redis, Docling, Stripe.

## What Is Not Completed
- A stable local backend verification loop.
- A trustworthy split between unit, integration, and service-backed test profiles.
- A canonical backend runbook that matches current env/runtime truth.

## Highest-Impact Findings
1. Backend local verification is blocked before assertions.
- `tests/conftest.py` imports `app.models`, but the import resolves into an installed third-party `app` module in the current environment.
- That incorrect import chain then crashes inside `nougat/albumentations`.
- This means current backend test health is not telling you whether ScholarForm code passes. It is mostly telling you that environment/package resolution is broken.

2. Runtime contract and local environment are misaligned.
- Repo contract says Python 3.12 only.
- Local backend environment is Python 3.11.9.
- Any backend debugging done in this state is lower-confidence than it should be.

3. The backend has more completed product surface than the older plans claim.
- That is good for delivery potential.
- It is bad for maintenance if documentation and verification do not catch up.

## Code Quality Notes
- Positive:
  - Good top-level package decomposition.
  - Migrations, services, and routers are reasonably separated.
  - Several product concerns are isolated into dedicated service modules rather than buried in route handlers.
- Weaknesses:
  - Some acceptance-critical behavior is only implied by code presence, not validated.
  - There are placeholder and future-facing branches across generation/agent modules.
  - Complex external-service integrations increase fragility without a stable fixture-mode test harness.

## Where The Backend Team Is Likely To Get Stuck
- Packaging and import resolution during testing.
- External-service orchestration in local and CI environments.
- AI-provider fallbacks that exist in code but are not routinely verified.
- Migration drift between local assumptions and actual Supabase schema state.
- Performance debugging before a stable correctness baseline exists.

## Backend Focus Order
1. Restore correct local import behavior and Python 3.12 parity.
2. Split test layers cleanly: pure unit, fixture-backed integration, live-service integration.
3. Add a minimal deterministic smoke suite for templates, documents status, preview, generator session CRUD.
4. Verify one end-to-end path per product mode before adding new feature work.
5. Rewrite backend setup docs to reflect current env names, ports, and runtime assumptions.
