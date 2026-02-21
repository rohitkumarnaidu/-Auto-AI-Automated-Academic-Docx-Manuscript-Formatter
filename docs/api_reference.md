# 📚 ScholarForm AI - API Reference

Base URL: `http://localhost:8000/api`

## 🔐 Authentication
Uses Supabase JWT Bearer Token authentication.
**Header:** `Authorization: Bearer <supabase_access_token>`

---

## 📄 Document Management

### 1. Upload Document
Initiates a new processing job.
- **Endpoint:** `POST /documents/upload`
- **Content-Type:** `multipart/form-data`
- **Auth:** Required (Bearer Token)
- **Parameters:**
  - `file`: Manuscript file (DOCX, PDF, TEX, TXT, HTML, MD, DOC) [Max 50MB]
  - `template_name`: Target template (e.g., `"IEEE"`, `"ACM"`, `"Springer"`, `"APA"`, `"Nature"`, `"none"`). Default: `"none"`.
  - `formatting_options`: JSON string with options (`add_page_numbers`, `add_borders`, `add_cover_page`, `generate_toc`, `page_size`).
- **Response (200):**
  ```json
  {
    "job_id": "uuid-string",
    "status": "processing",
    "message": "File uploaded successfully"
  }
  ```
- **Errors:** `400` (invalid file), `413` (too large), `401` (unauthenticated)

### 2. Batch Upload
Upload multiple documents at once.
- **Endpoint:** `POST /documents/batch-upload`
- **Auth:** Required
- **Parameters:**
  - `files`: Up to 10 files
  - `template`: Target template
- **Response (200):**
  ```json
  {
    "jobs": [{ "filename": "paper.pdf", "job_id": "uuid", "status": "processing" }],
    "total": 1
  }
  ```

### 3. List Documents
- **Endpoint:** `GET /documents`
- **Auth:** Optional (anonymous returns empty list)
- **Query Params:** `status`, `template`, `start_date`, `end_date`, `limit` (1-100), `offset`

### 4. Check Processing Status
- **Endpoint:** `GET /documents/{job_id}/status`
- **Response (200):**
  ```json
  {
    "job_id": "uuid",
    "status": "COMPLETED",
    "progress": 100,
    "current_stage": "PERSISTENCE"
  }
  ```

### 5. Get Preview (Structured Results)
- **Endpoint:** `GET /documents/{job_id}/preview`
- **Auth:** Required
- **Response:** Structured data with validation results, errors, warnings

### 6. Get Compare Data
- **Endpoint:** `GET /documents/{job_id}/compare`
- **Auth:** Required
- **Response:** Original vs formatted comparison data

### 7. Download Formatted Document
- **Endpoint:** `GET /documents/{job_id}/download`
- **Auth:** Required
- **Response:** Binary DOCX file stream

### 8. Submit Edit
- **Endpoint:** `POST /documents/{job_id}/edit`
- **Auth:** Required
- **Body:** `{ "sections": { "BODY": [...] } }`

### 9. Delete Document
- **Endpoint:** `DELETE /documents/{job_id}`
- **Auth:** Required (ownership enforced)

---

## 📡 SSE (Real-time Updates)

### Stream Processing Events
- **Endpoint:** `GET /stream/{job_id}`
- **Auth:** Optional
- **Response:** Server-Sent Events stream
  ```
  data: {"phase": "EXTRACTION", "status": "COMPLETED", "progress": 30}
  ```

---

## 📊 Metrics
- **Endpoint:** `GET /metrics`
- **Auth:** Required
- **Response:** Pipeline statistics, template usage, average processing time

## 💬 Feedback
- **Endpoint:** `POST /feedback`
- **Auth:** Required
- **Body:** `{ "job_id": "uuid", "rating": 5, "comment": "Great!" }`

## 🩺 System Health
- **Endpoint:** `GET /health`
- **Response:**
  ```json
  {
    "status": "healthy",
    "components": {
      "supabase": "connected",
      "redis": "connected"
    }
  }
  ```
