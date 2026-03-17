# Implementation Roadmap (Phases 0-5)

This roadmap outlines the exact sequence to transform this feature-rich but operationally unstable repository into a robust platform.

## Phase 0: Restore Truth & Fast Feedback (COMPLETE)
✅ Reconfigure Python 3.12 Virtual Environment.
✅ Resolve `pytest` backend import collisions (`pytest` passes).
✅ Fix frontend JSX syntactic bugs and Next.js Suspense limitations (`npm run build` passes).

## Phase 1: Canonical Documentation Reset (IN PROGRESS)
- Align all `docs/` files to physical truths (Next.js, Python 3.12, 34 page routes, etc).
- Remove obsolete references to Spring Boot or Vite defaults.

## Phase 2: Contract & Smoke Validation
- Implement API endpoint happy-path tests (Templates, Health, Session CRUD, Previews).
- Finalize Playwright assertions for Live Editor, Agent Chat, and Resut UI.

## Phase 3: Critical Gap Fixes
- Wire empty JavaScript stubs (`api.synthesis.js`).
- Complete backend `latex_exporter.py` functionality.
- Set up Production configurations (Render / Vercel hooks).
- Fix `globals.css` compiled Tailwind bloat.

## Phase 4: Service-Backed Validation
- Smoke test local Redis, Supabase, and Stripe interactions.
- Vet Docling Python fallback pipeline for PDF conversion limits.

## Phase 5: Launch Readiness
- Lock cloud topology (Vercel + Render + Supabase + Upstash).
- Apply system monitoring (Sentry.io).
