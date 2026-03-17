# UI Color And Focus Notes

## Direct Answer
Yes, some UI color and visual-system cleanup is worth doing, but `not before` build/test stabilization.

Right now the bigger risk is not that the UI is ugly. The bigger risk is that parts of the product are visually decent but operationally untrusted.

## Current UI Direction
- Formatter pages: generally coherent, clean, blue-primary academic SaaS direction.
- Live preview / AI sidebar: more aggressive violet-indigo accent language.
- Generator surfaces: richer and denser, but not fully unified with formatter surfaces.

## Recommendation
- `Do not` do a full visual redesign now.
- `Do` do a controlled UI-system pass after build/test fixes with these goals:
  - one primary brand palette
  - one secondary accent strategy
  - consistent icon sizing and button hierarchy
  - consistent empty, loading, warning, and error states

## Suggested Color Strategy
- Keep the current academic/productive base:
  - primary blue family for system actions and trust states
  - slate neutrals for structure
- Use AI accent sparingly:
  - keep violet/indigo only for explicitly AI-generated or assistant actions
  - do not let every generator/live-preview control drift into a separate sub-brand

## Practical UI Changes Worth Considering
1. Standardize primary buttons across formatter, generator, and settings.
2. Standardize status colors:
  - success: green
  - warning: amber
  - failure: red
  - AI accent: violet only where AI is actually acting
3. Remove hardcoded one-off visual choices where possible and move toward shared tokens.
4. Make live preview feel like part of the same product family as formatter results and editor pages.

## What To Focus On Before Color Tweaks
1. Green frontend build.
2. Restore unit-test baseline.
3. Validate route contracts.
4. Then do the UI system cleanup.

## Bottom Line
- Color changes are `recommended`, but not as a first priority.
- Visual unification is a `Phase 3` hardening task, not a `Phase 0` blocker.
