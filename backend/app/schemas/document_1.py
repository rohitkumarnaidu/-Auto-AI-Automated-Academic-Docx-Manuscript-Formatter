"""
document_1.py — Extended / v2 Document Schemas.

Extends the primary document schemas with additional fields for:
- Batch upload support
- Richer validation result structures
- AI analysis metadata
- Webhook / callback configuration
- Export job tracking

These schemas are used by extended API variants or future v2 endpoints.
They are fully backward-compatible with the primary document schemas.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

# Re-export everything from the primary schema
from app.schemas.document import (
    ExportFormat,
    DocumentStatus,
    PageSize,
    TemplateChoice,
    FormattingOptions,
    DocumentUploadResponse,
    PhaseStatus,
    DocumentStatusResponse,
    DocumentBase,
    Document,
    DocumentListItem,
    DocumentListResponse,
    DocumentMetaSummary,
    DocumentPreviewResponse,
    CompareOriginal,
    CompareFormatted,
    DocumentCompareResponse,
)

__all__ = [
    # Primary schemas (re-exported)
    "ExportFormat",
    "DocumentStatus",
    "PageSize",
    "TemplateChoice",
    "FormattingOptions",
    "DocumentUploadResponse",
    "PhaseStatus",
    "DocumentStatusResponse",
    "DocumentBase",
    "Document",
    "DocumentListItem",
    "DocumentListResponse",
    "DocumentMetaSummary",
    "DocumentPreviewResponse",
    "CompareOriginal",
    "CompareFormatted",
    "DocumentCompareResponse",
    # Extended schemas
    "FormattingOptionsV2",
    "BatchUploadRequest",
    "BatchUploadResponse",
    "ValidationIssue",
    "ValidationResultDetail",
    "AIAnalysisMetadata",
    "DocumentV2",
    "ExportJobRequest",
    "ExportJobResponse",
    "WebhookConfig",
    "DocumentEditRequest",
]


# ── Extended Formatting Options ───────────────────────────────────────────────

class FormattingOptionsV2(FormattingOptions):
    """
    Extended formatting options with fine-grained control.

    Adds: line spacing, font override, watermark, header/footer text.
    Fully backward-compatible with FormattingOptions.
    """

    line_spacing: float = Field(
        1.0,
        ge=1.0,
        le=3.0,
        description="Line spacing multiplier (1.0 = single, 1.5 = one-and-a-half, 2.0 = double).",
    )
    font_override: Optional[str] = Field(
        None,
        max_length=80,
        description="Override the body font (e.g. 'Times New Roman', 'Arial'). None = use template default.",
    )
    watermark_text: Optional[str] = Field(
        None,
        max_length=50,
        description="Diagonal watermark text (e.g. 'DRAFT', 'CONFIDENTIAL'). None = no watermark.",
    )
    header_text: Optional[str] = Field(
        None,
        max_length=200,
        description="Custom running header text. None = use template default.",
    )
    footer_text: Optional[str] = Field(
        None,
        max_length=200,
        description="Custom running footer text. None = use template default.",
    )
    include_abstract_box: bool = Field(
        False,
        description="Wrap the abstract in a styled box (IEEE-style).",
    )


# ── Batch Upload Schemas ──────────────────────────────────────────────────────

class BatchUploadItem(BaseModel):
    """A single file entry in a batch upload request."""

    filename: str = Field(..., description="Original filename.")
    template: TemplateChoice = Field("IEEE", description="Template to apply.")
    formatting_options: Optional[FormattingOptionsV2] = None


class BatchUploadRequest(BaseModel):
    """Request body for POST /api/documents/batch-upload."""

    files: List[BatchUploadItem] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="List of files to process (max 10 per batch).",
    )
    notify_on_complete: bool = Field(
        False,
        description="Send an email notification when all jobs complete.",
    )
    webhook_url: Optional[str] = Field(
        None,
        description="URL to POST a completion payload to when all jobs finish.",
    )


class BatchUploadResponse(BaseModel):
    """Returned after a successful batch upload request."""

    batch_id: str = Field(..., description="UUID identifying this batch.")
    job_ids: List[str] = Field(..., description="Individual job UUIDs, one per file.")
    total_files: int = Field(..., description="Number of files accepted.")
    message: str = Field(..., description="Human-readable confirmation.")


# ── Validation Result Schemas ─────────────────────────────────────────────────

class ValidationIssue(BaseModel):
    """A single validation error or warning."""

    level: Literal["error", "warning", "info"] = Field(
        ..., description="Severity of the issue."
    )
    code: str = Field(
        ...,
        description="Machine-readable issue code (e.g. 'MISSING_ABSTRACT', 'INVALID_DOI').",
    )
    message: str = Field(..., description="Human-readable description.")
    location: Optional[str] = Field(
        None,
        description="Where in the document the issue was found (e.g. 'Section: References').",
    )
    suggestion: Optional[str] = Field(
        None,
        description="Suggested fix for the issue.",
    )


class ValidationResultDetail(BaseModel):
    """Structured validation result with typed issues."""

    is_valid: bool = Field(..., description="True if no errors were found.")
    issues: List[ValidationIssue] = Field(
        default_factory=list,
        description="All errors, warnings, and info messages.",
    )
    error_count: int = Field(0, description="Number of error-level issues.")
    warning_count: int = Field(0, description="Number of warning-level issues.")
    checked_at: Optional[datetime] = Field(
        None, description="Timestamp when validation ran."
    )


# ── AI Analysis Metadata ──────────────────────────────────────────────────────

class AIAnalysisMetadata(BaseModel):
    """AI-generated metadata about the processed document."""

    detected_language: Optional[str] = Field(
        None, description="ISO 639-1 language code detected in the document."
    )
    detected_domain: Optional[str] = Field(
        None,
        description="Academic domain detected (e.g. 'Computer Science', 'Biology').",
    )
    readability_score: Optional[float] = Field(
        None, ge=0, le=100, description="Flesch-Kincaid readability score."
    )
    section_count: Optional[int] = Field(None, description="Number of sections detected.")
    figure_count: Optional[int] = Field(None, description="Number of figures detected.")
    table_count: Optional[int] = Field(None, description="Number of tables detected.")
    reference_count: Optional[int] = Field(None, description="Number of references detected.")
    equation_count: Optional[int] = Field(None, description="Number of equations detected.")
    confidence_score: Optional[float] = Field(
        None, ge=0.0, le=1.0,
        description="Overall AI confidence in the formatting result (0–1).",
    )
    model_used: Optional[str] = Field(
        None, description="Primary AI model used for processing (e.g. 'SciBERT + Llama-3')."
    )
    processing_time_ms: Optional[int] = Field(
        None, description="Total pipeline processing time in milliseconds."
    )


# ── Extended Document Schema ──────────────────────────────────────────────────

class DocumentV2(Document):
    """
    Extended document record with AI metadata and structured validation.

    Adds: ai_metadata, validation_detail, batch_id, webhook_url.
    Fully backward-compatible with Document.
    """

    ai_metadata: Optional[AIAnalysisMetadata] = Field(
        None, description="AI-generated analysis metadata."
    )
    validation_detail: Optional[ValidationResultDetail] = Field(
        None, description="Structured validation result with typed issues."
    )
    batch_id: Optional[str] = Field(
        None, description="Batch UUID if this job was part of a batch upload."
    )
    webhook_url: Optional[str] = Field(
        None, description="URL notified on job completion (if configured)."
    )

    model_config = ConfigDict(from_attributes=True)


# ── Export Job Schemas ────────────────────────────────────────────────────────

class ExportJobRequest(BaseModel):
    """Request body for POST /api/documents/{job_id}/export."""

    formats: List[ExportFormat] = Field(
        ...,
        min_length=1,
        description="List of formats to export (e.g. ['docx', 'pdf', 'jats']).",
    )
    include_metadata: bool = Field(
        True, description="Include a metadata JSON sidecar file in the export."
    )
    compress: bool = Field(
        False, description="Return a ZIP archive when multiple formats are requested."
    )


class ExportJobResponse(BaseModel):
    """Returned after an export job is queued."""

    export_id: str = Field(..., description="UUID of the export job.")
    job_id: str = Field(..., description="Source document job UUID.")
    formats: List[ExportFormat]
    status: str = Field("QUEUED", description="Export job status.")
    download_urls: Optional[Dict[str, str]] = Field(
        None,
        description="Map of format → download URL (populated when status is READY).",
    )


# ── Webhook Config ────────────────────────────────────────────────────────────

class WebhookConfig(BaseModel):
    """Webhook configuration for job completion notifications."""

    url: str = Field(..., description="HTTPS URL to POST the completion payload to.")
    secret: Optional[str] = Field(
        None,
        max_length=128,
        description="Optional HMAC secret for payload signature verification.",
    )
    events: List[Literal["job.completed", "job.failed", "batch.completed"]] = Field(
        default_factory=lambda: ["job.completed"],
        description="Events that trigger the webhook.",
    )
    retry_count: int = Field(
        3, ge=0, le=10, description="Number of retry attempts on webhook delivery failure."
    )


# ── Edit Request Schema ───────────────────────────────────────────────────────

class DocumentEditRequest(BaseModel):
    """Request body for POST /api/documents/{job_id}/edit."""

    edited_structured_data: Dict[str, Any] = Field(
        ...,
        description="The modified structured document data to re-format.",
    )
    re_validate: bool = Field(
        True,
        description="Run validation again after re-formatting.",
    )
    re_export: bool = Field(
        True,
        description="Re-generate the output file after re-formatting.",
    )
