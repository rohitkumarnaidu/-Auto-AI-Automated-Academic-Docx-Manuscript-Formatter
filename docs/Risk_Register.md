# Risk Register

This document tracks potential architectural, security, and operational risks identified in the Codex 5.4 Audit and ongoing assessments.

## Active Risks

### Red (High Impact / High Likelihood)
1. **Infrastructure Limits:** Free-tier Render instances (512MB RAM) are incompatible with the original GROBID Docker requirements (1.5GB RAM).
   - *Mitigation:* Established a 3-tier fallback strategy (Docling > PyMuPDF > PyPDF2).
2. **WebSocket Disconnects:** Live Editor (`/live`) relies on a WebSocket connection that may drop during cloud scaling or timeout thresholds.
   - *Mitigation:* Implement exponential backoff + reconnection queue. Needs immediate QA.
3. **Template Sync Drift:** The frontend currently defines the template whitelist statically rather than sourcing it from the backend APIs (`/api/v1/templates`).
   - *Mitigation:* Phase 3 will merge the API endpoint directly to the frontend selector.

### Yellow (Medium Impact / Manageable Likelihood)
4. **Security Blind Spots in Document Conversion:** Pandoc/LibreOffice subprocess invocations carry inherent risks of command injection or malicious inputs.
   - *Mitigation:* Implemented strict sanitization and limited file parsing. RBAC scaffolding exists but needs validation across endpoints.
5. **UI Component Consistency:** Next.js `/components` vs `/src/components` dual existence combined with "violet accent drift" causes technical debt and cognitive load.
   - *Mitigation:* Directory consolidation and strict semantic token application required.
6. **No Analytics System:** Blind operation without Posthog or Mixpanel.
   - *Mitigation:* Integrate a free tier analytics system prior to launch.
