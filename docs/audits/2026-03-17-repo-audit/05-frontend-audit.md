# Frontend Audit

## Current Strengths
- The frontend is already a sizable Next.js app-router application, not a small landing page shell.
- Rich editing, live preview, generator, account, billing, history, admin, and feedback surfaces are all represented.
- Theme state is centralized and persisted through the existing theme provider flow.
- Results, validation, and multi-step flows show meaningful UX investment.
- Playwright coverage inventory is already well beyond the older target count in raw file volume.

## What Is Completed
- Next.js app-router migration is already in place.
- ThemeContext + ThemeToggle unification is done.
- TipTap editor on `/edit` is done.
- Results quality panel is done.
- Live preview page/components/hooks are present.
- Generator multi-upload and agent pages/components are present.
- Billing/settings/profile/admin UI surfaces exist.
- `NEXT_PUBLIC_*` env usage is the dominant current pattern.
- `frontend/context` duplication described in older plans no longer appears to exist.

## What Is Completed But Needs Improvement
- UI consistency.
  - There is clear visual effort, but icon systems, palette choices, and component language are not fully unified across product areas.
- Accessibility trust.
  - Tests exist, but local verification is currently blocked by build/test defects.
- Route parity.
  - Breadth is high, but current build instability means route existence is not the same as route trust.
- E2E inventory.
  - Test count is high, but until the build and base unit harness are fixed, confidence is lower than raw numbers suggest.

## What Is Partially Completed
- Download/export contract consistency.
- Live preview production hardening.
- Generator flow acceptance proof.
- Template-editor cloud/local behavior clarity.
- Some product areas still mix feature-flagged behavior with partially exposed UI expectations.

## What Is Not Completed
- A clean green production build.
- A reliable local unit-test baseline.
- A canonical frontend documentation story.

## Highest-Impact Findings
1. Frontend build is currently red.
- `npm run build` fails on `frontend/generate-tests.js`.
- This is a release blocker and a CI blocker.

2. Frontend unit test base setup is broken.
- `npm test` fails because `@testing-library/dom` is missing.
- This is a foundational harness issue, not a behavior-level failure.

3. The frontend is more complete than the planning docs claim.
- Plans saying live preview is 0 percent or that `/edit` is still textarea-only are no longer accurate.
- This changes prioritization: the right move is hardening and truth-alignment, not re-implementing already-built surfaces.

## UX / UI Quality Review
- Strong points:
  - Rich surface area.
  - Real product feeling rather than placeholder pages.
  - Light/dark support is treated as a first-class concern.
  - Results and generator pages have meaningful information architecture.
- Weak points:
  - Visual language is not yet fully standardized across formatter, live preview, and generator experiences.
  - The live editor AI sidebar introduces a stronger violet accent language than the rest of the app, which may be intentional but currently feels only partially systematized.
  - Some route/service contracts look inconsistent enough to warrant explicit smoke testing, especially export flows.

## Accessibility Notes
- Positive:
  - There are dedicated accessibility-oriented E2E specs.
  - Focus-management components and form-label coverage exist.
- Risks:
  - Current build/test instability means accessibility maturity cannot be trusted solely from file presence.
  - Responsive and keyboard behavior should be re-verified after the build is fixed.

## Where The Frontend Team Is Likely To Get Stuck
- Hidden build breaks from utility scripts that sit outside core route files.
- Drift between hardcoded frontend template lists and backend template truth.
- Complex route-level state without a stable smoke harness.
- Shipping visually polished but contract-inconsistent export/generator flows.

## Frontend Focus Order
1. Fix the production build blocker in `generate-tests.js`.
2. Restore unit-test base dependencies and rerun the small trusted Vitest subset.
3. Verify route-by-route build integrity.
4. Align live preview and export contracts with backend truth.
5. Standardize template sourcing, UX copy, and visual language across formatter/generator/live-preview flows.
