"""
auth_1.py — Extended / v2 Auth Schemas.

Extends the primary auth schemas with additional fields for:
- Institutional SSO / OAuth flows
- Multi-factor authentication (MFA) support
- Richer signup metadata (country, role preference, referral source)
- Structured error responses

These schemas are used by extended API variants or future v2 endpoints.
They are fully backward-compatible with the primary auth schemas.
"""

from typing import Literal, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator

# Re-export everything from the primary schema so importers can use either file
from app.schemas.auth import (
    SignupRequest,
    LoginRequest,
    ForgotPasswordRequest,
    VerifyOTPRequest,
    ResetPasswordRequest,
    AuthTokenResponse,
    MessageResponse,
    OTPVerifyResponse,
    _validate_password_strength,
)

__all__ = [
    # Primary schemas (re-exported)
    "SignupRequest",
    "LoginRequest",
    "ForgotPasswordRequest",
    "VerifyOTPRequest",
    "ResetPasswordRequest",
    "AuthTokenResponse",
    "MessageResponse",
    "OTPVerifyResponse",
    # Extended schemas
    "SignupRequestV2",
    "LoginRequestV2",
    "MFAChallengeRequest",
    "MFAVerifyRequest",
    "SSOCallbackRequest",
    "AuthErrorResponse",
    "RefreshTokenRequest",
    "RefreshTokenResponse",
]


# ── Extended Request Schemas ──────────────────────────────────────────────────

class SignupRequestV2(SignupRequest):
    """
    Extended signup request with additional metadata fields.

    Adds: country, role_preference, referral_source, and newsletter opt-in.
    Fully backward-compatible with SignupRequest.
    """

    country: Optional[str] = Field(
        None,
        max_length=100,
        description="User's country (ISO 3166-1 alpha-2 or full name).",
        examples=["IN", "US", "GB"],
    )
    role_preference: Optional[Literal["researcher", "student", "faculty", "industry"]] = Field(
        None,
        description="User's primary role — used to personalise the experience.",
    )
    referral_source: Optional[str] = Field(
        None,
        max_length=200,
        description="How the user heard about ScholarForm AI (optional).",
        examples=["Google Search", "Conference", "Colleague"],
    )
    newsletter_opt_in: bool = Field(
        False,
        description="Whether the user wants to receive product updates via email.",
    )


class LoginRequestV2(LoginRequest):
    """
    Extended login request that supports MFA and device fingerprinting.

    Adds: mfa_token, device_id, remember_me.
    Fully backward-compatible with LoginRequest.
    """

    mfa_token: Optional[str] = Field(
        None,
        min_length=6,
        max_length=8,
        description="TOTP/HOTP token for MFA-enabled accounts (optional).",
    )
    device_id: Optional[str] = Field(
        None,
        max_length=128,
        description="Client device fingerprint for session tracking (optional).",
    )
    remember_me: bool = Field(
        False,
        description="If true, request a long-lived refresh token.",
    )


class MFAChallengeRequest(BaseModel):
    """Request to initiate an MFA challenge for an already-authenticated session."""

    user_id: str = Field(..., description="UUID of the authenticated user.")
    factor_id: str = Field(..., description="MFA factor ID from Supabase.")


class MFAVerifyRequest(BaseModel):
    """Request to verify an MFA challenge response."""

    user_id: str = Field(..., description="UUID of the authenticated user.")
    factor_id: str = Field(..., description="MFA factor ID from Supabase.")
    challenge_id: str = Field(..., description="Challenge ID returned by the MFA challenge endpoint.")
    code: str = Field(
        ...,
        min_length=6,
        max_length=8,
        description="TOTP/HOTP code from the authenticator app.",
    )


class SSOCallbackRequest(BaseModel):
    """Request body for the OAuth/SSO callback endpoint."""

    provider: Literal["google", "github", "microsoft", "orcid"] = Field(
        ...,
        description="OAuth provider that initiated the SSO flow.",
    )
    code: str = Field(..., description="Authorization code returned by the OAuth provider.")
    state: Optional[str] = Field(None, description="CSRF state token (if used).")
    redirect_uri: Optional[str] = Field(
        None, description="Redirect URI used in the original OAuth request."
    )


class RefreshTokenRequest(BaseModel):
    """Request to refresh an expired access token."""

    refresh_token: str = Field(..., description="Long-lived refresh token from a previous login.")


# ── Extended Response Schemas ─────────────────────────────────────────────────

class AuthErrorResponse(BaseModel):
    """Structured error response for auth endpoint failures."""

    success: bool = Field(False)
    error_code: str = Field(
        ...,
        description="Machine-readable error code (e.g. 'INVALID_CREDENTIALS', 'OTP_EXPIRED').",
        examples=["INVALID_CREDENTIALS", "OTP_EXPIRED", "ACCOUNT_LOCKED"],
    )
    message: str = Field(..., description="Human-readable error description.")
    retry_after: Optional[int] = Field(
        None,
        description="Seconds to wait before retrying (for rate-limited responses).",
    )


class RefreshTokenResponse(BaseModel):
    """Returned after a successful token refresh."""

    access_token: str = Field(..., description="New Supabase JWT access token.")
    token_type: str = Field(default="bearer")
    expires_in: Optional[int] = Field(None, description="New token lifetime in seconds.")
