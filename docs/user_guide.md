# ScholarForm User Guide

## 1. Overview

ScholarForm helps you upload an academic manuscript, apply a journal template, validate structure, and export final output.

Supported upload file types:

- `.docx`
- `.pdf`
- `.tex`

Maximum file size: `50 MB`.

## 2. UI Walkthrough (Screenshot Slots)

Add screenshots to the paths below and keep the filenames the same.

![Landing Page](./screenshots/01-landing-page.png)
![Upload Page](./screenshots/02-upload-page.png)
![Processing Status](./screenshots/03-processing-status.png)
![Preview Page](./screenshots/04-preview-page.png)
![Download Page](./screenshots/05-download-page.png)

## 3. End-to-End Workflow

1. Open the app and go to `Upload`.
2. Upload a valid manuscript (`.docx`, `.pdf`, `.tex`).
3. Select a template (for example `IEEE`, `APA`, or `None`).
4. Set processing options (page numbers, cover page, TOC, page size).
5. Click `Process Document`.
6. Wait for the job to complete.
7. Review in:
   - `Compare Results`
   - `Preview Document`
8. Open `Download` and export in the required format.

## 4. Export Options

Available export formats:

- DOCX
- PDF
- JSON

Use the export dialog in `Download` page to choose output format.

## 5. Security Features

The frontend now includes:

- client-side file type validation (`.docx`, `.pdf`, `.tex` only)
- user input sanitization before API submit
- CSRF token header support (`X-CSRF-Token`) with cookie/session fallback

## 6. Common User Errors

- Invalid file type:
  Upload only `.docx`, `.pdf`, `.tex`.
- File too large:
  Keep file size under `50 MB`.
- Download failed:
  Retry after processing is complete; check network connection.

## 7. Quick Checklist for New Users

- Use one of the supported file formats.
- Wait for status to become `COMPLETED`.
- Use `Preview` before final export.
- Export in the format required by the target journal.
