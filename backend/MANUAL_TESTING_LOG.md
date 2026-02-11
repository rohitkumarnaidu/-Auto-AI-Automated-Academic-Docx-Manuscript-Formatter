# MANUAL TESTING LOG

## 1. Purpose
This document is for **stability validation**, **crash prevention**, and **lifecycle correctness** of the ScholarForm AI backend. It tracks manual verification of the document processing pipeline's runtime behavior.

> [!IMPORTANT]
> - This log does NOT validate feature completeness.
> - This log does NOT validate AI correctness (NLP/Explanations).
> - This log does NOT replace automated testing (intentionally excluded per project policy).

---

## 2. Test Cases (Static)

### [TC-01] Document Upload & Initial Job Creation
- **Description**: Verify the backend accepts a DOCX file and initiates an asynchronous job.
- **Swagger Steps**:
  1. Open `POST /api/documents/upload`.
  2. Click "Try it out".
  3. Upload a `.docx` file in the `file` field.
  4. Set `template` to `IEEE` (or leave default).
  5. Execute.
- **Expected Outcome**: HTTP 200/201 response with a `job_id` and status `RUNNING`.
- **Failure Indicator**: HTTP 500, crash in terminal, or missing `job_id`.

### [TC-02] Asynchronous Status Polling
- **Description**: Verify that the status endpoint returns granular phase updates.
- **Swagger Steps**:
  1. Copy the `job_id` from TC-01.
  2. Open `GET /api/documents/{job_id}/status`.
  3. Click "Try it out", paste the `job_id`.
  4. Execute multiple times during processing.
- **Expected Outcome**: Response shows `status` (RUNNING -> COMPLETED) and `current_phase` updates.
- **Failure Indicator**: Status stuck at `UPLOAD`, HTTP 404, or terminal exception.

### [TC-03] Server Reload Handling (Crash Prevention)
- **Description**: Verify the orchestrator marks jobs as failed when the server reloads.
- **Steps**:
  1. Start TC-01.
  2. While status is `RUNNING`, trigger a server reload (e.g., save any `.py` file).
  3. Wait for reload.
  4. Call TC-02 for the same `job_id`.
- **Expected Outcome**: Status returns `FAILED` with message "Interrupted by server reload".
- **Failure Indicator**: Status remains `RUNNING` or terminal shows unhandled `asyncio.CancelledError`.

### [TC-04] Database Interrupt Resilience
- **Description**: Verify the status endpoint handles database unavailability gracefully.
- **Steps**:
  1. Open `GET /api/documents/{job_id}/status`.
  2. Temporarily stop the local database or disconnect network.
  3. Execute in Swagger.
- **Expected Outcome**: HTTP 200 with status `UNSTABLE` and message "Database connection interrupted. Retrying...".
- **Failure Indicator**: HTTP 500 or application crash.

### [TC-05] Document Edit Re-processing
- **Description**: Verify the non-destructive edit flow.
- **Swagger Steps**:
  1. Open `POST /api/documents/{job_id}/edit`.
  2. Paste a valid `job_id`.
  3. Use the JSON payload below.
- **Expected Outcome**: HTTP 200 with status `RUNNING`. Subsequent status poll shows `PERSISTENCE` -> `COMPLETED`.
- **Sample JSON Payload**:
```json
{
  "edited_structured_data": {
    "sections": {
      "ABSTRACT": ["This is a manually edited abstract test."],
      "INTRODUCTION": ["Introduction text after manual edit."]
    }
  }
}
```

---

## 3. Test Execution Log (Append-Only)

*Note: Execution entries are added only after explicit manual testing by the user.*

| Date | Tester | Test IDs | Result | Notes |
|------|--------|----------|--------|-------|
