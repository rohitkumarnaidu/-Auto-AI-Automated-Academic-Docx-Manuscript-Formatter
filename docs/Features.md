# ScholarForm AI — Features List

## Formatter Mode A (Upload & Format)
- ✅ 9-format file upload (DOCX, PDF, ODT, TeX, HTML, MD, TXT, RTF, DOC)
- ✅ MIME + magic byte + extension tri-validation
- ✅ Pipeline: Parse → Structure Detect → Block Classify → NLP → Validate → Format → Export
- ✅ 17 journal templates
- ✅ DOCX + PDF export
- ⚠️ LaTeX export (stub — 743B file)
- ✅ Processing stepper animation
- ✅ Quality score calculation (backend service exists)
- ⚠️ Quality score display (needs verification)
- ⚠️ TipTap editor on /edit (needs verification)
- ⚠️ Batch upload (component exists, wiring needs testing)
- ⚠️ Template editor save (needs API connection verification)

## Formatter Mode B (Live Preview)
- ✅ WebSocket handler (`preview.py`)
- ✅ Preview renderer with cache (`preview_renderer.py` — 15.6KB)
- ✅ Redis pub/sub realtime (`pubsub.py`, `events.py`)
- ✅ SplitEditor component (9.8KB)
- ✅ PreviewPane component (3.5KB)
- ✅ useLivePreviewSocket hook (5.5KB)
- ✅ /formatter/live page
- ⚠️ AI sidebar (needs runtime testing)

## Generator Mode A (Multi-Doc Synthesis)
- ✅ Session service (generator_session_service.py — 6.8KB)
- ✅ Session vector store / ChromaDB RAG (7.8KB)
- ✅ Synthesizer pipeline (24.2KB)
- ✅ SSE event streaming (v1/synthesis.py — 8.8KB)
- ✅ MultiUploadPanel component (11.4KB)
- ✅ SynthesisStageTimeline component (6KB)
- ❌ api.synthesis.js (36B — empty stub)

## Generator Mode B (AI Agent)
- ✅ Task parser (6.2KB)
- ✅ Agent pipeline (34KB — most substantial file)
- ✅ Section prompts (3.4KB)
- ✅ Quality scorer (4.5KB)
- ✅ Citation assembly service (4.9KB)
- ✅ OutlineApproval (10.7KB)
- ✅ AgentChatPane (11KB)
- ✅ TokenStream (11.3KB)
- ✅ DocumentBuildPane (6.6KB)
- ✅ SessionHistory (8KB)
- ✅ /agent page

## Security & Auth
- ✅ Supabase Auth (JWT, OTP, OAuth Google/GitHub)
- ✅ JWKS JWT verifier (5.4KB)
- ⚠️ RBAC middleware (708B — stub)
- ✅ Rate limiting (6.9KB + 4.1KB tier-aware)
- ✅ Security headers (4.6KB)
- ✅ Abuse detection (2.7KB)
- ✅ Virus scanner (4.4KB)
- ⚠️ Audit logging (1.1KB — minimal)

## Billing
- ✅ Stripe webhook router (v1/billing.py — 3.8KB)
- ✅ Plan tier utility (planTier.js — 2.5KB)
- ✅ Upgrade modal (3.7KB)
- ⚠️ Settings billing tab (needs verification)

## CI/CD & DevOps
- ✅ backend-ci.yml, frontend-ci.yml, security.yml
- ✅ deploy-production.yml, e2e-production.yml
- ❌ deploy-staging.yml (missing)
- ❌ Grafana dashboards

## UX Features
- ✅ Dark/light mode (ThemeContext)
- ✅ Onboarding tour (6.8KB)
- ✅ Error boundary (3.6KB)
- ✅ 93 E2E test files (many are stubs)
- ✅ Notification bell
- ✅ Feedback form
