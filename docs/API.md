# ScholarForm AI — API Reference

> **Base URL:** `http://localhost:8000` (dev) | `https://api.scholarform.ai` (prod)  
> **Auth:** `Authorization: Bearer <supabase_access_token>` on authenticated routes  
> **Versioning:** `/api/v1/` prefix. Legacy routes (without `/v1/`) carry `Deprecation` response headers.  
> **Last Updated:** March 2026 (Codex 5.4 Audit — cross-checked against `backend/app/routers/v1/`)

---

## Response Envelope (All v1 Endpoints)

All v1 responses follow the standard envelope:
```json
{
  "success": true,
  "data": { ... },
  "request_id": "abc-123"
}
```

Error responses:
```json
{
  "success": false,
  "error": { "code": "VALIDATION_ERROR", "message": "..." },
  "request_id": "abc-123"
}
```

---

## Formatter Endpoints (`v1/documents.py` — 10.3KB)

### POST /api/v1/documents/upload
Upload and process a document.
```
Content-Type: multipart/form-data
Body: file (binary), template (string), options (JSON)

Response: { success: true, data: { job_id, status: "processing" } }
```
- **Runtime evidence:** ✅ File exists, core pipeline tested
- **Virus scanning** runs before processing (ClamAV)
- Returns `job_id` in <400ms; processing continues in background

### GET /api/v1/documents/{job_id}/status
Poll processing status.
```
Response: { success: true, data: { status, progress, current_stage, stages[] } }
```
- `status` values: `queued`, `processing`, `completed`, `failed`
- **Runtime evidence:** ✅ Used by frontend `Stepper.jsx`

### GET /api/v1/documents/{job_id}/preview
Get rendered HTML preview (read-only, no DOCX).
```
Response: { success: true, data: { html, css } }
```

### GET /api/v1/documents/{job_id}/compare
Before/after diff view (Codex-confirmed route).
```
Response: { success: true, data: { original_html, formatted_html, diff } }
```

### GET /api/v1/documents/{job_id}/download
Download processed document.
```
Query: format=docx|pdf|latex
Response: Binary file download (signed URL) or redirect
```
- **LaTeX:** ⚠️ Partial — `latex_exporter.py` is a stub (743B)

### POST /api/v1/documents/{job_id}/edit
Save TipTap editor content back to job.
```
Body: { content: "<html>..." }
Response: { success: true, data: { saved: true } }
```

### GET /api/v1/documents
List user's documents (paginated).
```
Query: page, limit
Response: { success: true, data: { items[], total, page } }
```

### DELETE /api/v1/documents/{id}
Delete a document and its associated storage files.

---

## Template Endpoints (`v1/templates.py` — 4.8KB)

### GET /api/v1/templates
List all 17 templates with metadata and preview CSS.
```
Response: { success: true, data: [{ name, displayName, description, preview_css }] }
```
- **Runtime evidence:** ✅ Whitelist confirmed complete in `document.py` schema

### GET /api/v1/templates/{name}
Get a specific template's rules and preview CSS.
```
Response: { success: true, data: { name, rules, preview_css } }
```

---

## Generator Endpoints (`v1/generator.py` — 18.8KB)

### POST /api/v1/generator/sessions
Create a generator session (multi-doc or AI agent).
```
Body: { session_type: "synthesis"|"agent", template, config, prompt? }
Files: (multipart for multi-doc synthesis)
Response: { success: true, data: { session_id, status: "started" } }
```

### GET /api/v1/generator/sessions/{id}
Get session state and progress.

### GET /api/v1/generator/sessions/{id}/events
SSE stream for real-time progress events.
```
Event format: data: { event_type, payload, timestamp }
Event types: stage_update, token, outline_ready, error, complete
```

### POST /api/v1/generator/sessions/{id}/messages
Send a message for agent chat or RAG Q&A.
```
Body: { content: "..." }
```

### POST /api/v1/generator/sessions/{id}/outline/approve
Approve generated outline to proceed to section generation.
```
Response: SSE stream begins writing sections
```

---

## Synthesis Endpoints (`v1/synthesis.py` — 8.8KB)

### POST /api/v1/synthesis/sessions
Create a multi-doc synthesis session.
```
Body: multipart (2-6 PDF files)
Response: { success: true, data: { session_id } }
```

### GET /api/v1/synthesis/sessions/{id}/events
SSE stream for synthesis pipeline stages.

---

## Live Preview (WebSocket)

### WS /api/v1/preview/ws/{session_id}
Real-time preview WebSocket connection.
```
Client → Server: { content: "<editor content>", template: "ieee" }
Server → Client: { html: "<rendered>", css: "...", timestamp }
```
- **Render strategy:** HTML-only (no DOCX). Target RTT: <80ms.
- **Runtime evidence:** ✅ `preview.py` (7.4KB), `preview_renderer.py` (15.6KB)

---

## Auth Endpoints

### POST /api/v1/auth/signup
### POST /api/v1/auth/login
Supabase Auth proxied endpoints (JWT/OTP/OAuth).

---

## Billing Endpoints (`v1/billing.py` — 3.8KB)

### POST /api/v1/billing/webhook
Stripe webhook handler. Requires `STRIPE_WEBHOOK_SECRET` in env.
- **Runtime evidence:** ✅ File exists; Stripe CLI validation needed

### GET /api/v1/billing/portal
Stripe billing portal redirect URL.

---

## Health & Metrics

### GET /api/v1/health
```json
{
  "status": "ok",
  "services": { "redis": "ok", "db": "ok", "chromadb": "ok" }
}
```

### GET /metrics
Prometheus metrics endpoint (not authenticated).

---

## Deprecated Endpoints

Legacy routes (without `/v1/` prefix) are still active but return a `Deprecation` response header. See `backend/app/routers/deprecation.py` (1.6KB). Clients should migrate to `/api/v1/` paths.
