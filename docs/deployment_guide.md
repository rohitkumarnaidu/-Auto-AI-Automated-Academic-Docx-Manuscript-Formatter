# 🚀 ScholarForm AI - Deployment Guide

This guide covers the deployment of the ScholarForm AI platform using Docker Compose and local development setups.

## 📋 Prerequisites
- **Docker Engine** (v20.10+)
- **Docker Compose** (v2.0+)
- **Python** (3.11+) - *For local dev only*
- **Node.js** (v18+) - *For local dev only*

---

## 🐳 Docker Deployment (Recommended)

The easiest way to run the full stack (Backend, Frontend, Redis, Grobid, Celery) is via Docker Compose.

### 1. Build and Start
Navigate to the `backend/docker` directory (or root if using the root compose file):
```bash
cd backend/docker
docker-compose up --build -d
```
*Note: The first build may take 5-10 minutes to compile dependencies and pull the Grobid image.*

### 2. Verify Services
Check running containers:
```bash
docker-compose ps
```

| Service | Port | Description |
| :--- | :--- | :--- |
| `backend` | `8000` | FastAPI Server |
| `frontend` | `3000`/`5173`| React Interface |
| `grobid` | `8070` | PDF Extraction Service |
| `redis` | `6379` | Cache & Message Broker |
| `celery_worker`| N/A | Async Task Processor |

### 3. Access Application
- **Frontend:** [http://localhost:5173](http://localhost:5173) (or 3000 depending on config)
- **API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Grobid:** [http://localhost:8070](http://localhost:8070)

### 4. Stop Services
```bash
docker-compose down
```

---

## 🛠️ Local Development Setup

### Backend
1. **Navigate:** `cd backend`
2. **Virtual Env:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
3. **Install:**
   ```bash
   pip install -r requirements.txt
   ```
   *(Ensure you have LibreOffice installed for PDF conversion)*
4. **Env Setup:**
   Copy `.env.example` to `.env` and configure:
   ```ini
   REDIS_URL=redis://localhost:6379/0
   GROBID_SERVER_URL=http://localhost:8070
   ```
5. **Run:**
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend
1. **Navigate:** `cd frontend`
2. **Install:**
   ```bash
   npm install
   ```
3. **Run:**
   ```bash
   npm run dev
   ```

---

## 🔧 Troubleshooting

### "Grobid not available"
- Ensure the `grobid` container is running and healthy.
- Check `backend` logs: `docker-compose logs backend`.
- Verify network connectivity between containers.

### "Redis connection failed"
- Ensure `redis` container is up.
- Check `REDIS_URL` in `.env`.

### Rate Limiting 429 Errors
- The default limit is 10 uploads/min.
- Wait a minute or restart Redis to clear counters if testing manually.
