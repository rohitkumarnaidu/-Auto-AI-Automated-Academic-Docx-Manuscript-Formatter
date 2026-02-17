# Troubleshooting Guide

## 1. Upload Errors

### Error: Invalid file type

Cause:

- Uploaded file is not `.docx`, `.pdf`, or `.tex`.

Fix:

- Convert your document to one of the supported formats.
- Re-upload using the `Upload` page.

### Error: File too large

Cause:

- File exceeds `50 MB`.

Fix:

- Compress images inside the manuscript.
- Split appendices into separate files.

## 2. Processing Issues

### Status does not move from RUNNING

Cause:

- backend worker delay
- temporary DB/network issue

Fix:

1. Refresh the page.
2. Check backend logs.
3. Re-run with the same file.

### Job failed during formatting

Cause:

- malformed input document
- template mismatch

Fix:

1. Try with `None` template once.
2. Re-run with target template.
3. Check `backend/app/routers/documents.py` logs.

## 3. Preview Problems

### Preview empty or partial

Cause:

- structured content missing
- API request failed

Fix:

- retry preview page
- check network tab for `/api/documents/{job_id}/preview`
- verify document reached `COMPLETED` status

## 4. Download Problems

### Download button fails

Cause:

- output not ready
- temporary network/server error

Fix:

1. Confirm status is `COMPLETED`.
2. Retry download from `Download` page.
3. Try DOCX first, then PDF/JSON.

### PDF unavailable

Cause:

- PDF conversion dependency missing on backend host.

Fix:

- ensure LibreOffice is available on server/runtime.

## 5. Auth / Security Errors

### 401 Unauthorized

Fix:

- log out and log in again.

### CSRF token mismatch

Cause:

- stale cookies/session

Fix:

1. Clear site cookies.
2. Refresh app.
3. Retry request.

## 6. XSS / Input Sanitization Notes

Input fields are sanitized before API submission. If special characters are stripped:

- avoid pasting raw HTML tags into normal text fields
- use plain text for title, name, and metadata fields

## 7. Debug Commands

Frontend:

```bash
cd frontend
npm run test
npm run build
```

Backend:

```bash
cd backend
python -m pytest tests/test_template_renderer.py
python -m pytest tests/test_export_pipeline.py --no-cov
```

## 8. Escalation Checklist

When raising a bug, include:

- input file type and size
- template selected
- exact error message
- job id
- browser + OS
