# 🎓 ScholarForm AI — Automated Academic Manuscript Formatter

> Transform your research into publication-ready documents in minutes using AI-powered formatting and validation.

## ✨ Features

- **Multi-format ingestion:** DOCX, PDF, LaTeX, TXT, HTML, Markdown, DOC
- **Publisher templates:** IEEE, ACM, Springer, APA, Nature (+ custom template editor)
- **AI-powered pipeline:** SciBERT classification, NVIDIA NIM semantic audit, language detection
- **Smart extraction:** Nougat OCR fallback for scanned PDFs, GROBID/Docling integration
- **Multi-column layout:** Contract-driven column configs (2-col body, 1-col abstract)
- **Real-time progress:** SSE streaming with 6-step pipeline status
- **Batch upload:** Process up to 10 documents at once
- **Validation report:** Errors, warnings, AI recommendations

## 🤖 AI/ML Stack

| Component | Model / Tool | Purpose |
|-----------|-------------|---------|
| **SciBERT** | `allenai/scibert_scivocab_uncased` | Academic section classification |
| **NVIDIA NIM** | Llama 3.3 70B Instruct | Structure analysis, compliance checks |
| **NVIDIA NIM** | Llama 3.2 11B Vision | Figure/table quality analysis |
| **DeepSeek R1** | Via Ollama | Local inference fallback |
| **RAG Engine** | BGE-M3 + ChromaDB | Style guide rule retrieval |
| **GROBID** | Self-hosted | PDF header/reference extraction |
| **Docling** | IBM | Document structure analysis |
| **Nougat** | Meta | OCR for scanned PDFs |
| **langdetect** | | Document language detection |

## 🔧 Required Environment Variables

```env
# Supabase (Required)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret

# Frontend
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
VITE_API_URL=http://localhost:8000

# AI Services (Optional — graceful degradation)
NVIDIA_API_KEY=nvapi-xxx
OLLAMA_BASE_URL=http://localhost:11434
GROBID_URL=http://localhost:8070

# Infrastructure (Optional)
REDIS_URL=redis://localhost:6379/0
CROSSREF_MAILTO=your-email@example.com
```

## 🚀 Quick Start

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 📁 Project Structure

```
automated-manuscript-formatter/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entrypoint
│   │   ├── pipeline/            # Core processing pipeline
│   │   │   ├── orchestrator.py  # Job orchestration
│   │   │   ├── parsing/         # DOCX, PDF, LaTeX, Nougat parsers
│   │   │   ├── classification/  # SciBERT + rule-based classifier
│   │   │   ├── intelligence/    # SemanticParser, RAG engine
│   │   │   ├── formatting/      # Contract-driven DOCX formatter
│   │   │   └── validation/      # Template compliance validator
│   │   ├── routers/             # API endpoints
│   │   ├── services/            # NVIDIA, CrossRef, Supabase clients
│   │   └── templates/           # Publisher configs (contract.yaml)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/               # Upload, Processing, Dashboard, etc.
│   │   ├── components/          # Navbar, Stepper, FileUpload, etc.
│   │   ├── context/             # Auth, Document, Theme providers
│   │   └── services/api.js      # API client with retry/debounce
│   └── package.json
└── docs/                        # Architecture, API reference
```

## 📄 License
MIT
