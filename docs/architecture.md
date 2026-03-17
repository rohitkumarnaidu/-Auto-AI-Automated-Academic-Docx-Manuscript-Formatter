# ScholarForm AI — Architecture

## System Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    BROWSER (Next.js 14)                      │
│  Auth │ Formatter UI │ Generator UI │ Live Editor │ Admin    │
├─────────────────────────────────────────────────────────────┤
│                  API GATEWAY (Optional: FastAPI)         │
│  JWKS JWT Verify │ Rate Limit │ Request ID │ CORS           │
├─────────────────────────────────────────────────────────────┤
│               BACKEND (FastAPI + Uvicorn)                    │
│  v1 Routers │ Middleware │ Security │ Background Tasks       │
├──────────────┬───────────────┬──────────────────────────────┤
│  Pipeline    │   Services    │   Realtime                   │
│  12-Stage    │   LLM Service │   Redis Pub/Sub              │
│  Formatter   │   Auth Service│   WebSocket                  │
│  Synthesizer │   Generator   │   SSE Events                 │
│  Agent       │   Quality     │                              │
├──────────────┴───────────────┴──────────────────────────────┤
│              DATA LAYER                                      │
│  PostgreSQL (Supabase) │ Redis │ ChromaDB │ Supabase Storage │
├─────────────────────────────────────────────────────────────┤
│              EXTERNAL SERVICES                               │
│  NVIDIA NIM │ Groq │ Ollama │ ClamAV │ GROBID │ Stripe     │
└─────────────────────────────────────────────────────────────┘
```

## Request Flows

### Formatter Mode A — Upload & Format
```
Browser → POST /api/v1/documents/upload
  → Virus Scan (ClamAV)
  → Validate (MIME + Magic + Extension)
  → Start Background Task (Celery/asyncio)
  → Return job_id (< 400ms)

Background:
  → Parse (GROBID/python-docx) 
  → Structure Detection
  → Block Classification (SciBERT)
  → NLP Enhancement (YAKE/spaCy)
  → Validation
  → Format & Render (Template)
  → Export (DOCX/PDF)
  → SSE: {stage, progress}
```

### Formatter Mode B — Live Preview
```
Browser ↔ WebSocket /api/v1/preview/ws/{id}
  → Client sends edited content + template
  → Server: HTML render (< 80ms, no DOCX!)
  → Redis cache: preview:{id}
  → Server sends rendered HTML/CSS
```

### Generator Mode B — AI Agent
```
Browser → POST /api/v1/generator/sessions
  → Create session in DB
  → Return session_id

Browser → POST .../messages (user prompt)
  → Task Parser (LLM: extract requirements)
  → Outline Generation (LLM: structured JSON)
  → SSE: outline for approval

Browser → POST .../outline/approve
  → Section-by-section generation (LLM streaming)
  → SSE: token stream per section
  → Citation assembly (CrossRef)
  → Quality scoring
  → DOCX render
```

## Key Architecture Decisions
1. **No DOCX on live preview** — HTML/CSS only for < 80ms latency
2. **No LLM during typing** — only on explicit user action
3. **Redis pub/sub as backbone** — single pattern for SSE + WebSocket + Celery
4. **LiteLLM abstraction** — same client code for all LLM providers
5. **Background tasks for > 400ms ops** — never block request thread
