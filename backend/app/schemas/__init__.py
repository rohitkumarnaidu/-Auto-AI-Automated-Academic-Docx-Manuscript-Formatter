"""
app/schemas/__init__.py

Central import hub for all Pydantic schemas.

Primary schemas (v1):
  from app.schemas import SignupRequest, Document, User, ...

Extended schemas (v2):
  from app.schemas import SignupRequestV2, DocumentV2, UserWithPreferences, ...

All schemas are available from this single import point.
"""

# ── Auth ──────────────────────────────────────────────────────────────────────
from app.schemas.auth import (
    SignupRequest,
    LoginRequest,
    ForgotPasswordRequest,
    VerifyOTPRequest,
    ResetPasswordRequest,
    AuthTokenResponse,
    MessageResponse,
    OTPVerifyResponse,
)

# ── Auth v2 ───────────────────────────────────────────────────────────────────
from app.schemas.auth_1 import (
    SignupRequestV2,
    LoginRequestV2,
    MFAChallengeRequest,
    MFAVerifyRequest,
    SSOCallbackRequest,
    RefreshTokenRequest,
    RefreshTokenResponse,
    AuthErrorResponse,
)

# ── Document ──────────────────────────────────────────────────────────────────
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

# ── Document v2 ───────────────────────────────────────────────────────────────
from app.schemas.document_1 import (
    FormattingOptionsV2,
    BatchUploadRequest,
    BatchUploadResponse,
    ValidationIssue,
    ValidationResultDetail,
    AIAnalysisMetadata,
    DocumentV2,
    ExportJobRequest,
    ExportJobResponse,
    WebhookConfig,
    DocumentEditRequest,
)

# ── User ──────────────────────────────────────────────────────────────────────
from app.schemas.user import (
    UserBase,
    User,
    UserProfile,
    UserUpdateRequest,
)

# ── User v2 ───────────────────────────────────────────────────────────────────
from app.schemas.user_1 import (
    UserQuota,
    UserUsageStats,
    NotificationPreferences,
    UserPreferences,
    UserWithPreferences,
    AdminUserView,
    APIKey,
    APIKeyCreateRequest,
    APIKeyCreateResponse,
    UserListResponse,
)

__all__ = [
    # Auth v1
    "SignupRequest",
    "LoginRequest",
    "ForgotPasswordRequest",
    "VerifyOTPRequest",
    "ResetPasswordRequest",
    "AuthTokenResponse",
    "MessageResponse",
    "OTPVerifyResponse",
    # Auth v2
    "SignupRequestV2",
    "LoginRequestV2",
    "MFAChallengeRequest",
    "MFAVerifyRequest",
    "SSOCallbackRequest",
    "RefreshTokenRequest",
    "RefreshTokenResponse",
    "AuthErrorResponse",
    # Document v1
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
    # Document v2
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
    # User v1
    "UserBase",
    "User",
    "UserProfile",
    "UserUpdateRequest",
    # User v2
    "UserQuota",
    "UserUsageStats",
    "NotificationPreferences",
    "UserPreferences",
    "UserWithPreferences",
    "AdminUserView",
    "APIKey",
    "APIKeyCreateRequest",
    "APIKeyCreateResponse",
    "UserListResponse",
]
