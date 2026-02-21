# ScholarForm AI - System Architecture

## High-Level Overview
ScholarForm AI is an automated manuscript formatting platform that ingests academic documents, runs parsing + validation + formatting pipelines, and returns template-compliant outputs.

---

## Core Components

### 1. FastAPI Backend
- API routers for documents, auth, stream, feedback, and metrics
- Request validation, auth checks, and job orchestration

### 2. Pipeline Orchestrator
- Coordinates ingestion, extraction, NLP/analysis, validation, and formatting
- Updates document/job status and progress during execution

### 3. Parsing + Extraction
- Multi-format parsing: DOCX, PDF, TEX, TXT, HTML, MD, DOC
- GROBID and Docling integrations for richer structure extraction

### 4. AI / ML Stack
- SciBERT for academic section classification
- NVIDIA NIM models:
  - Llama 3.3 70B (text reasoning/audit)
  - Llama 3.2 11B Vision (figure/table analysis)
- DeepSeek R1 via Ollama for local inference fallback
- RAG pipeline using BGE-M3 embeddings + vector retrieval

### 5. Validation + Formatting
- Contract/template-aware rules (IEEE, Springer, APA, ACM, Nature, etc.)
- Formatting options (page numbers, borders, cover page, TOC, page size)
- Export outputs for downstream preview/download

### 6. Infrastructure
- **FastAPI BackgroundTasks** for job processing
- **In-memory event queue + SSE** for live progress updates
- **Supabase PostgreSQL** for persistence (documents, results, user-linked records)
- Frontend: React + Vite + Tailwind

---

## Data Flow
1. User uploads a file from frontend.
2. Backend validates file and creates a job record.
3. Background task executes parser -> analysis -> validation -> formatter.
4. Progress updates are published via SSE.
5. Preview/compare/download endpoints expose processed outputs.
