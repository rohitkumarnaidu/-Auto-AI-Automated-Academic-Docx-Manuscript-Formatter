"""
user_1.py — Extended / v2 User Schemas.

Extends the primary user schemas with additional fields for:
- Admin user management
- Usage statistics and quotas
- Notification preferences
- API key management

These schemas are used by extended API variants or future v2 endpoints.
They are fully backward-compatible with the primary user schemas.
"""

from datetime import datetime
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# Re-export everything from the primary schema
from app.schemas.user import (
    UserBase,
    User,
    UserProfile,
    UserUpdateRequest,
)

__all__ = [
    # Primary schemas (re-exported)
    "UserBase",
    "User",
    "UserProfile",
    "UserUpdateRequest",
    # Extended schemas
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


# ── Usage & Quota Schemas ─────────────────────────────────────────────────────

class UserQuota(BaseModel):
    """Processing quota limits for a user."""

    max_documents_per_month: int = Field(
        50, description="Maximum documents the user can process per calendar month."
    )
    max_file_size_mb: int = Field(
        50, description="Maximum file size in MB per upload."
    )
    max_batch_size: int = Field(
        10, description="Maximum number of files per batch upload."
    )
    priority_processing: bool = Field(
        False, description="Whether the user gets priority queue placement."
    )
    plan: Literal["free", "pro", "enterprise"] = Field(
        "free", description="Subscription plan tier."
    )


class UserUsageStats(BaseModel):
    """Aggregated usage statistics for a user."""

    documents_this_month: int = Field(0, description="Documents processed in the current month.")
    documents_total: int = Field(0, description="Total documents processed since account creation.")
    pages_processed_total: int = Field(0, description="Total pages processed across all documents.")
    last_active_at: Optional[datetime] = Field(None, description="Last API activity timestamp.")
    favourite_template: Optional[str] = Field(
        None, description="Most frequently used template."
    )
    average_processing_time_ms: Optional[float] = Field(
        None, description="Average pipeline processing time in milliseconds."
    )


# ── Preferences Schemas ───────────────────────────────────────────────────────

class NotificationPreferences(BaseModel):
    """User notification settings."""

    email_on_complete: bool = Field(
        True, description="Send email when a document finishes processing."
    )
    email_on_failure: bool = Field(
        True, description="Send email when a document fails processing."
    )
    email_newsletter: bool = Field(
        False, description="Receive product updates and tips."
    )
    in_app_notifications: bool = Field(
        True, description="Show in-app notifications for job events."
    )


class UserPreferences(BaseModel):
    """User interface and workflow preferences."""

    default_template: str = Field(
        "IEEE", description="Default journal template for new uploads."
    )
    default_page_size: Literal["Letter", "A4", "Legal"] = Field(
        "Letter", description="Default page size for formatted output."
    )
    auto_download: bool = Field(
        False, description="Automatically download the output file when processing completes."
    )
    show_validation_warnings: bool = Field(
        True, description="Display validation warnings in the UI (not just errors)."
    )
    theme: Literal["light", "dark", "system"] = Field(
        "system", description="UI colour theme preference."
    )
    notifications: NotificationPreferences = Field(
        default_factory=NotificationPreferences,
        description="Notification settings.",
    )


# ── Extended User Schemas ─────────────────────────────────────────────────────

class UserWithPreferences(UserProfile):
    """
    Full user record with preferences and usage data.

    Used by the /api/users/me/full endpoint.
    Fully backward-compatible with UserProfile.
    """

    preferences: UserPreferences = Field(
        default_factory=UserPreferences,
        description="User's saved preferences.",
    )
    quota: UserQuota = Field(
        default_factory=UserQuota,
        description="User's processing quota.",
    )
    usage: Optional[UserUsageStats] = Field(
        None, description="Aggregated usage statistics."
    )

    model_config = ConfigDict(from_attributes=True)


class AdminUserView(UserWithPreferences):
    """
    Full user record visible to administrators only.

    Adds: is_banned, ban_reason, internal_notes, supabase_metadata.
    Never expose this schema to non-admin users.
    """

    is_banned: bool = Field(False, description="Whether the account is suspended.")
    ban_reason: Optional[str] = Field(None, description="Reason for account suspension.")
    internal_notes: Optional[str] = Field(
        None, description="Admin-only notes about this user."
    )
    supabase_metadata: Optional[Dict] = Field(
        None, description="Raw Supabase user metadata (admin only)."
    )

    model_config = ConfigDict(from_attributes=True)


# ── API Key Schemas ───────────────────────────────────────────────────────────

class APIKey(BaseModel):
    """A user's API key record (key value is never returned after creation)."""

    id: str = Field(..., description="UUID of the API key.")
    name: str = Field(..., description="Human-readable label for the key.")
    prefix: str = Field(..., description="First 8 characters of the key (for identification).")
    created_at: datetime = Field(..., description="When the key was created.")
    last_used_at: Optional[datetime] = Field(None, description="When the key was last used.")
    expires_at: Optional[datetime] = Field(None, description="Key expiry timestamp (None = never).")
    is_active: bool = Field(True, description="Whether the key is currently active.")
    scopes: List[str] = Field(
        default_factory=list,
        description="Permission scopes granted to this key (e.g. ['documents:read', 'documents:write']).",
    )


class APIKeyCreateRequest(BaseModel):
    """Request body for POST /api/users/me/api-keys."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=80,
        description="Human-readable label for the new key.",
    )
    expires_in_days: Optional[int] = Field(
        None,
        ge=1,
        le=365,
        description="Key lifetime in days. None = never expires.",
    )
    scopes: List[str] = Field(
        default_factory=lambda: ["documents:read", "documents:write"],
        description="Permission scopes to grant.",
    )


class APIKeyCreateResponse(BaseModel):
    """Returned once after API key creation. The full key is never shown again."""

    id: str = Field(..., description="UUID of the new API key.")
    name: str
    key: str = Field(
        ...,
        description="Full API key value. Store this securely — it will not be shown again.",
    )
    prefix: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    scopes: List[str]


# ── Admin List Schema ─────────────────────────────────────────────────────────

class UserListResponse(BaseModel):
    """Returned by GET /api/admin/users."""

    users: List[AdminUserView] = Field(default_factory=list)
    total: int = Field(0, description="Total matching users (before pagination).")
    limit: int = Field(50)
    offset: int = Field(0)
