# ScholarForm AI — API Reference

**Base URL:** `http://localhost:8000` (dev) | `https://api.scholarform.ai` (prod)  
**Auth:** `Authorization: Bearer <supabase_access_token>` on authenticated routes  
**Versioning:** `/api/v1/` prefix. Legacy routes have `Deprecation` headers.

## Formatter Endpoints

### POST /api/v1/documents/upload
Upload and process a document.
```
Content-Type: multipart/form-data
Body: file (binary), template (string), options (JSON)
Response: { success: true, data: { job_id, status: "processing" } }
```

### GET /api/v1/documents/{job_id}/status
Poll processing status.
```
Response: { success: true, data: { status, progress, current_stage, stages[] } }
```

### GET /api/v1/documents/{job_id}/download
Download processed document.
```
Query: format=docx|pdf|latex
Response: Binary file download (signed URL)
```

### GET /api/v1/documents
List user's documents (paginated).

### DELETE /api/v1/documents/{id}
Delete a document.

## Template Endpoints

### GET /api/v1/templates
List all 17 templates with metadata.

### GET /api/v1/templates/{name}
Get template details and preview CSS.

## Generator Endpoints

### POST /api/v1/generator/sessions
Create a generator session (multi-doc or agent).
```
Body: { session_type, template, config, prompt? }
Files: (multipart for multi-doc)
Response: { session_id, status: "started" }
```

### GET /api/v1/generator/sessions/{id}
Get session state.

### GET /api/v1/generator/sessions/{id}/events
SSE stream for real-time progress events.

### POST /api/v1/generator/sessions/{id}/messages
Send message for RAG Q&A or agent chat.

### POST /api/v1/generator/sessions/{id}/outline/approve
Approve generated outline to proceed.

## Live Preview Endpoints

### WebSocket /api/v1/preview/ws/{session_id}
Live preview WebSocket connection.
```
Client sends: { content, template }
Server sends: { html, css, timestamp }
```

## Auth Endpoints

### POST /api/v1/auth/signup, /api/v1/auth/login
Supabase Auth proxied endpoints.

## Billing Endpoints

### POST /api/v1/billing/webhook
Stripe webhook handler.

### GET /api/v1/billing/portal
Stripe billing portal redirect.

## Health Endpoints

### GET /api/v1/health
```
Response: { status: "ok", services: { redis, db, chromadb } }
```

### GET /metrics
Prometheus metrics endpoint.
