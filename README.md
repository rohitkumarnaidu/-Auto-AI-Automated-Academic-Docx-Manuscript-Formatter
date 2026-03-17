# ScholarForm AI - Automated Academic Manuscript Formatter

ScholarForm AI formats academic manuscripts into publisher-ready outputs using deterministic rules plus AI-assisted analysis.

## AI/ML Stack
- **SciBERT** (`allenai/scibert_scivocab_uncased`) for section/semantic classification
- **NVIDIA NIM**:
  - Llama 3.3 70B Instruct (text reasoning and compliance analysis)
  - Llama 3.2 11B Vision (figure/table analysis)
- **DeepSeek R1 via Ollama** for local inference fallback
- **RAG with BGE-M3** embeddings for style-rule retrieval
- **GROBID** for PDF metadata/reference extraction
- **Docling** for fast, high-quality document PDF/OCR fallback structure extraction

## Required Environment Variables

**Backend (`backend/.env`):**
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_JWT_SECRET`
- `SUPABASE_SERVICE_ROLE_KEY`
- `NVIDIA_API_KEY`
- `OLLAMA_BASE_URL` (optional)
- `GROBID_ENABLED=true` (ensure you have local GROBID running)

**Frontend (`frontend/.env.local`):**
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- `NEXT_PUBLIC_API_URL`

## Quick Setup

### 1. Backend Setup
```bash
cd backend
python -m venv .venv
# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Mac/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
```

Set backend env vars in `backend/.env`.

Run backend API:
```bash
uvicorn app.main:app --reload --port 8000
```
API docs available at: `http://localhost:8000/docs`

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open web app at: `http://localhost:3000`

## Core API Endpoints
- `POST /api/v1/documents/upload`
- `GET /api/v1/documents/{job_id}/status`
- `GET /api/v1/documents/{job_id}/preview`
- `GET /api/v1/documents/{job_id}/compare`
- `GET /api/v1/documents/{job_id}/download`
- `POST /api/v1/documents/{job_id}/edit`
- `GET /api/v1/templates`
- `GET /api/v1/health`
