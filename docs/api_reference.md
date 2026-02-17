# 📚 ScholarForm AI - API Reference

Base URL: `http://localhost:8000/api`

## 🔐 Authentication
The API uses Bearer Token authentication.
**Header:** `Authorization: Bearer <token>`
*(Note: For the MLP, simple token simulation is used. See `verify_rate_limit.py` for examples)*

---

## 📄 Document Management

### 1. Upload Document
Initiates a new processing job.
- **Endpoint:** `POST /documents/upload`
- **Content-Type:** `multipart/form-data`
- **Rate Limit:** 10 requests/minute per user.
- **Parameters:**
  - `file`: The manuscript file (PDF, DOCX, TEX, etc.) [Max 50MB]
  - `template_name`: (Optional) Target formatting template (e.g., "IEEE", "Nature"). Default: "IEEE".
- **Response (200 OK):**
  ```json
  {
    "job_id": "uuid-string",
    "status": "processing",
    "message": "File uploaded successfully"
  }
  ```
- **Errors:**
  - `429 Too Many Requests`: Rate limit exceeded.
  - `413 Payload Too Large`: File exceeds 50MB.
  - `415 Unsupported Media Type`: Invalid file extension.

### 2. Check Processing Status
Get the real-time status of a job.
- **Endpoint:** `GET /documents/{job_id}/status`
- **Response (200 OK):**
  ```json
  {
    "job_id": "uuid-string",
    "status": "COMPLETED",
    "progress": 100,
    "current_stage": "PERSISTENCE",
    "message": "All results persisted."
  }
  ```

### 3. Get Structured Results
Retrieve the parsed, analyzed, and validated data.
- **Endpoint:** `GET /documents/{job_id}/result`
- **Response (200 OK):**
  ```json
  {
    "document_id": "uuid-string",
    "structured_data": { ... },
    "validation_results": {
      "is_valid": true,
      "errors": [],
      "warnings": [],
      "ai_semantic_audit": { ... }
    }
  }
  ```

### 4. Export Formatted Document
Download the final formatted manuscript.
- **Endpoint:** `GET /documents/{job_id}/export`
- **Query Params:**
  - `format`: `docx` (default), `pdf`, `jats`, `md`, `json`.
- **Response:** Binary file stream (Download).

---

## ⚡ WebSocket (Real-time)
Connect for live progress updates.
- **URL:** `ws://localhost:8000/ws/{client_id}`
- **Events:**
  - `{"type": "progress", "job_id": "...", "progress": 45, "status": "NLP_ANALYSIS"}`
  - `{"type": "error", "job_id": "...", "message": "..."}`
  - `{"type": "complete", "job_id": "...", "output_url": "..."}`

---

## 🩺 System Health
- **Endpoint:** `GET /health`
- **Response:**
  ```json
  {
    "status": "healthy",
    "components": {
      "redis": "connected",
      "grobid": "available",
      "database": "connected"
    }
  }
  ```
