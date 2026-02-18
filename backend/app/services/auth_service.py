import logging
from typing import Optional

import jwt
from fastapi import HTTPException, status
from app.config.settings import settings

logger = logging.getLogger(__name__)

# ── Supabase client (lazy, safe) ───────────────────────────────────────────────
# If credentials are missing the server still starts; auth endpoints return 503.
try:
    from supabase import create_client, Client as SupabaseClient
    if settings.SUPABASE_URL and settings.SUPABASE_ANON_KEY:
        supabase: Optional[SupabaseClient] = create_client(
            settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY
        )
        logger.info("✅ Supabase client initialised.")
    else:
        supabase = None
        logger.warning(
            "⚠️  SUPABASE_URL or SUPABASE_ANON_KEY not set. "
            "Auth endpoints will return 503 until credentials are configured."
        )
except Exception as _exc:
    supabase = None
    logger.error("❌ Failed to initialise Supabase client: %s", _exc)


def _require_supabase():
    """Raise HTTP 503 if the Supabase client is not available."""
    if supabase is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service is not configured. Please set SUPABASE_URL and SUPABASE_ANON_KEY.",
        )

class AuthService:
    @staticmethod
    def decode_token(token: str) -> dict:
        """
        Decodes and verifies the Supabase JWT.
        Validates signature, expiration (exp), audience (aud), and issuer (iss).
        """
        try:
            # Construct issuer URL from SUPABASE_URL if provided
            # Standard Supabase issuer is: https://<project-ref>.supabase.co/auth/v1
            supabase_url = settings.SUPABASE_URL
            expected_issuer = f"{supabase_url}/auth/v1" if supabase_url else None

            payload = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=[settings.ALGORITHM],
                audience="authenticated",
                issuer=expected_issuer,
                options={
                    "verify_exp": True,
                    "verify_iss": True if expected_issuer else False
                }
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidIssuerError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token issuer",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    def get_user_id_from_payload(payload: dict) -> str:
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing user identity (sub)",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_id

    @staticmethod
    async def signup(email: str, password: str, full_name: str, institution: str):
        _require_supabase()
        try:
            response = supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "full_name": full_name,
                        "institution": institution,
                    }
                },
            })
            return response
        except HTTPException:
            raise
        except Exception as exc:
            logger.error("Signup failed for %s: %s", email, exc)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            )

    @staticmethod
    async def login(email: str, password: str):
        _require_supabase()
        try:
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password,
            })
            return response
        except HTTPException:
            raise
        except Exception as exc:
            logger.warning("Login failed for %s: %s", email, exc)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(exc),
            )

    @staticmethod
    async def forgot_password(email: str):
        _require_supabase()
        try:
            # Supabase dashboard email template should be configured to send a 6-digit OTP code.
            response = supabase.auth.reset_password_for_email(email)
            return response
        except HTTPException:
            raise
        except Exception as exc:
            logger.error("Forgot-password failed for %s: %s", email, exc)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            )

    @staticmethod
    async def reset_password(email: str, otp: str, new_password: str):
        _require_supabase()
        try:
            # Step 1: Re-verify OTP to get a temporary session
            supabase.auth.verify_otp({
                "email": email,
                "token": otp,
                "type": "recovery",
            })
            # Step 2: Update the password
            response = supabase.auth.update_user({"password": new_password})
            return response
        except HTTPException:
            raise
        except Exception as exc:
            logger.error("Password reset failed for %s: %s", email, exc)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Reset failed: {str(exc)}",
            )

    @staticmethod
    async def verify_otp(email: str, token: str):
        _require_supabase()
        try:
            # Validates the recovery OTP without creating a long-lived session for the client
            response = supabase.auth.verify_otp({
                "email": email,
                "token": token,
                "type": "recovery",
            })
            return response
        except HTTPException:
            raise
        except Exception as exc:
            logger.warning("OTP verification failed for %s: %s", email, exc)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Verification failed: {str(exc)}",
            )
