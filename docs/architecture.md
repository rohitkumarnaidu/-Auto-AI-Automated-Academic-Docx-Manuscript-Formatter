# 🏗️ ScholarForm AI - System Architecture

## 🔭 High-Level Overview
ScholarForm AI is an agentic document processing platform that automates academic manuscript formatting. It uses a multi-stage pipeline orchestrated by AI agents to parse, analyze, validate, and reformat documents according to strict publisher standards (IEEE, ACM, Springer, Nature, APA).

---

## 🧩 Core Components

### 1. Orchestrator (`app/pipeline/orchestrator.py`)
The central nervous system. Manages the lifecycle of a document job, dispatching tasks to specialized agents and ensuring state consistency.
- **Responsibilities:** State management, error handling, pipeline sequencing, progress reporting.

### 2. Processing Pipeline
The pipeline consists of sequential stages:

- **Phase 1: Ingestion**
  - **Input:** PDF, DOCX, DOC, LaTeX, Markdown, TXT, HTML.
  - **Conversion:** Non-parseable inputs converted to intermediate DOCX via Pandoc/LibreOffice.
  - **Nougat OCR fallback:** Scanned PDFs with empty text blocks automatically re-processed via Nougat.

- **Phase 2: Extraction**
  - **Tools:** `ParserFactory` (auto-selects DOCX, PDF, LaTeX, HTML, Markdown, Nougat parsers), `GrobidClient`, `DoclingClient`.
  - **Task:** Extract raw text, metadata (title, authors), layout info, and structure into `Block` objects.

- **Phase 3: NLP & Analysis**
  - **Tools:** `SciBERT` (Semantic Classification via `SemanticParser`), `ContentClassifier` (rule-based + NLP fallback).
  - **Language Detection:** `langdetect` identifies non-English documents and switches to heuristic-only mode.
  - **Task:** Classify blocks (Abstract, Methodology, References, Footnotes, Appendix), detect headings and equations.

- **Phase 4: Validation**
  - **Tools:** `DocumentValidator`, `CrossRefClient`, `CSL Engine`, `NvidiaClient` (Llama 3.3 70B for semantic audit).
  - **Task:** Verify compliance with target template, citation formats, image quality.
  - **Output:** Validation Report (Errors/Warnings) + AI Semantic Advice.

- **Phase 5: Formatting & Export**
  - **Tools:** `Formatter` (python-docx with contract-driven styling), `PdfExporter`.
  - **Multi-column layout:** Contract YAML files define column layouts (e.g., 2-col body, 1-col abstract for IEEE/ACM).
  - **Task:** Apply styles, generate final DOCX output.

### 3. Intelligence Layer
- **NVIDIA NIM API:** Llama 3.3 70B (text analysis), Llama 3.2 11B Vision (figure analysis).
- **DeepSeek R1:** Accessed via Ollama for local inference.
- **RAG Engine:** Retrieves style guide rules from vector store (BGE-M3 embeddings + ChromaDB).
- **SciBERT:** Fine-tuned transformer for academic section classification.

### 4. Infrastructure
- **FastAPI:** High-performance async backend API.
- **FastAPI BackgroundTasks:** Async pipeline job execution (no Celery needed for single-server deployment).
- **SSE (Server-Sent Events):** Real-time progress updates via in-memory event queue.
- **Redis:** Caching layer for Grobid/CrossRef results and rate limiting.
- **Supabase PostgreSQL:** Persistence for job history, results, and user data.
- **React + Vite:** Modern frontend with Tailwind CSS.

---

## 🔄 Data Flow

1. **User** uploads file → **API** (auth + validation) → **Orchestrator** (start background job).
2. **BackgroundTask** → **ParserFactory** (extraction) → **Nougat fallback** (if empty blocks).
3. **Pipeline** → **SemanticParser** (language detection + SciBERT) → **ContentClassifier** (blocks).
4. **Pipeline** → **Validator** (template compliance + NVIDIA AI) → **Supabase** (persist results).
5. **Frontend** (SSE) ← **API** (progress updates from event queue).
6. **Pipeline** → **Formatter** (multi-column DOCX) → **File System**.
7. **User** downloads/previews/compares result.

---

## 🛡️ Security Layers
- **Auth:** Supabase JWT validation, ownership enforcement on mutations.
- **Edge:** Rate Limiting (10 req/min), CORS.
- **App:** Magic bytes validation (PDF/DOCX), file size limits, path sanitization.
- **Audit:** Bandit security scanning.
