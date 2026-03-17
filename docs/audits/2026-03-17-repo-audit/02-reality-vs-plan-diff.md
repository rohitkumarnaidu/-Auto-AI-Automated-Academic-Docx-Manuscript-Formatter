# Reality Vs Plan Diff

## Planning Claims That Are Already Outdated

| Claim In Plans / Docs | Current Repo Reality | Classification | Impact |
| --- | --- | --- | --- |
| CI/CD is absent | `.github/workflows/backend-ci.yml`, `frontend-ci.yml`, `security.yml`, deploy workflows already exist | Stale claim | Causes wrong prioritization |
| Live preview is 0 percent / not built | Backend preview router, websocket flow, frontend `/live` page, split editor, AI sidebar are already present | Stale claim | Understates actual product surface |
| `/edit` still uses a basic textarea | TipTap editor is already implemented on `/edit` | Stale claim | Misdirects frontend work |
| Theme toggle still needs unification | `ThemeContext` and `ThemeToggle` are already wired together | Stale claim | Duplicate work risk |
| Template whitelist still missing `resume` and `portfolio` | Both are already in router whitelist and enum set | Stale claim | Wastes review/debug time |
| Groq tier is missing | Groq fields exist in settings and fallback chain exists in `llm_service.py` | Stale claim | Misstates AI fallback readiness |
| Generator persistence is still in-memory only | `GeneratorSessionService` plus migration-backed session/message/document tables exist | Stale claim | Underestimates backend maturity |
| FastAPI needs a Spring Boot gateway now | No gateway project exists; FastAPI owns runtime today | Planning drift | Can create architecture churn |
| Frontend is Vite-based and uses `VITE_*` env vars | Frontend is Next.js and `.env.example` uses `NEXT_PUBLIC_*` vars | Stale docs | Breaks onboarding and deployment |
| Frontend local URL is `5173` | Next.js default local URL is `3000` | Stale docs | Misleads testers and new contributors |

## Requirements That Still Look Valid But Need Better Proof
- Antivirus scan before pipeline execution.
- Signed downloads and billing flows.
- Generator and synthesis end-to-end behavior.
- SciBERT accuracy and performance claims.
- CI as a true gate, not just files checked into `.github/workflows`.
- Live preview latency and reconnect guarantees.

## Repo Reality That The Plans Understate
- Route count and page surface are already much larger than the plans imply.
- Playwright test inventory already exceeds the 50-plus target in raw file count.
- Security posture is better scaffolded than the plans claim: CSP, rate limiting, JWKS verifier, audit logging service, signed download support, security workflow, and runbooks are present.
- Architecture documentation maturity is mixed: ADRs and runbooks exist, but top-level/generator docs are stale and contradictory.

## Repo Reality That The Plans Overstate
- The repo is not locally green. Build/test reliability is materially weaker than the plans assume.
- Several implemented features are still only `code-present`, not `runtime-proven`.
- Local environment readiness is behind the repo contract, especially for backend Python version and test setup.

## Practical Interpretation
- Use the repo, not the older plans, as the engineering baseline.
- Use the master plan and external markdown files as a requirements reservoir, not a progress dashboard.
- Treat stale plan items as `document drift`, not open engineering work.
- Rebuild the product roadmap around current blockers: verification, documentation truth, and end-to-end proof.
