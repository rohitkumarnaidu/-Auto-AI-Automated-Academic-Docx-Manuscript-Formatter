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
- **Docling** for document structure extraction

## Required Environment Variables

Backend:
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_JWT_SECRET`
- `NVIDIA_API_KEY`
- `OLLAMA_BASE_URL`

Frontend:
- `VITE_SUPABASE_URL`
- `VITE_SUPABASE_ANON_KEY`
- `VITE_API_BASE_URL`

## Quick Setup

1. Install dependencies:
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

2. Set backend env vars in `backend/.env`.

3. Run backend:
```bash
uvicorn app.main:app --reload --port 8000
```

4. Install and run frontend:
```bash
cd ../frontend
npm install
npm run dev
```

5. Open app:
- Frontend: `http://localhost:5173`
- API docs: `http://localhost:8000/docs`

## Core Endpoints
- `POST /api/documents/upload`
- `GET /api/documents/{job_id}/status`
- `GET /api/documents/{job_id}/preview`
- `GET /api/documents/{job_id}/compare`
- `GET /api/documents/{job_id}/download`
- `POST /api/documents/{job_id}/edit`
