# 🏗️ ScholarForm AI - System Architecture

## 🔭 High-Level Overview
ScholarForm AI is an agentic document processing platform designed to automate the formatting of academic manuscripts. It uses a multi-stage pipeline orchestrated by AI agents to parse, analyze, validate, and reformat documents according to strict academic standards (e.g., IEEE, Nature).

---

## 🧩 Core Components

### 1. Orchestrator (`app/pipeline/orchestrator.py`)
The central nervous system. It manages the lifecycle of a document job, dispatching tasks to specialized agents/services and ensuring state consistency.
- **Responsibilities:** State management, error handling, pipeline sequencing, progress reporting.

### 2. Processing Pipeline
The pipeline consists of linear and parallel stages:

- **Phase 1: Ingestion**
  - **Input:** PDF, DOCX, LaTeX, Markdown.
  - **Conversion:** All inputs converted to intermediate DOCX/Text/JSON.

- **Phase 2: Extraction (Agent A)**
  - **Tools:** `GrobidClient`, `DoclingClient`.
  - **Task:** Extract raw text, metadata (title, authors), layout info (bounding boxes), and structure.

- **Phase 3: NLP & Analysis**
  - **Tools:** `SciBERT` (Semantic Classification), `StructureDetector`.
  - **Task:** Classify blocks (Abstract, Methodology, etc.), detect headings, equations, and figures.

- **Phase 4: Validation (Agent B)**
  - **Tools:** `DocumentValidator`, `CrossRefClient`, `CSL Engine`.
  - **Task:** Verify compliance with target template (Heading levels, Citation formats, Image quality).
  - **Output:** Validation Report (Errors/Warnings) + Semantic Advice.

- **Phase 5: Formatting & Export**
  - **Tools:** `Formatter` (docxtpl), `Exporter` (LibreOffice).
  - **Task:** Apply styles, generate final DOCX/PDF/JATS.

### 3. Intelligence Layer
- **LangChain Agents:** Autonomous decision makers for complex edge cases.
- **RAG Engine:** Retrieves specific style guide rules (from VectorStore) to inform validation logic.
- **Deep Learning:** Used for figure analysis and pattern recognition (future integration).

### 4. Infrastructure
- **FastAPI:** High-performance async Backend API.
- **Redis:** Caching layer for Grobid results and Rate Limiting state.
- **Celery:** Distributed task queue for long-running pipeline jobs.
- **PostgreSQL/SQLite:** Persistence for job history and results.
- **React:** Modern frontend for user interaction and real-time preview.

---

## 🔄 Data Flow

1. **User** uploads file ➔ **API** (Rate Check) ➔ **Orchestrator** (Start Job).
2. **Orchestrator** ➔ **Celery** (Async Worker).
3. **Worker** ➔ **Grobid/Docling** (Extraction) ➔ **Redis** (Cache Results).
4. **Worker** ➔ **NLP Engine** (Analysis) ➔ **Database** (Update Status).
5. **Frontend** (WebSocket) ⬅️ **Redis/API** (Progress Updates).
6. **Worker** ➔ **Formatter** (Generate Output) ➔ **File System**.
7. **User** downloads result.

---

## 🛡️ Security Layers
- **Edge:** Rate Limiting (10 req/min), CORS.
- **App:** Input Validation (Size/Type), Path Sanitization.
- **Audit:** Bandit Security Scanning.
