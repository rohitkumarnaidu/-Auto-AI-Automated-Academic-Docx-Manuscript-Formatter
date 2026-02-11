
from fastapi import APIRouter, Depends, HTTPException, status
from app.utils.dependencies import get_current_user
from app.schemas.user import User
from app.schemas.auth import SignupRequest, LoginRequest, ForgotPasswordRequest, ResetPasswordRequest, VerifyOTPRequest
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Test endpoint to verify authentication.
    Returns the authenticated user's information from the token.
    """
    return current_user

@router.post("/signup")
async def signup(request: SignupRequest):
    """
    Triggers Supabase signup flow.
    Ensures terms_accepted is handled by schema validation.
    """
    return await AuthService.signup(request.email, request.password, request.full_name, request.institution)

@router.post("/login")
async def login(request: LoginRequest):
    """
    Triggers Supabase login flow. Returns session info (access_token).
    """
    return await AuthService.login(request.email, request.password)

@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    """
    Triggers Supabase forgot password flow (OTP-based).
    """
    return await AuthService.forgot_password(request.email)

@router.post("/verify-otp")
async def verify_otp(request: VerifyOTPRequest):
    """
    Verifies an OTP sent via email (Step 2 of Reset Password).
    Stateless verification.
    """
    return await AuthService.verify_otp(request.email, request.otp)

@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """
    Step 3 of Reset Password: Re-verifies OTP and updates password.
    """
    return await AuthService.reset_password(request.email, request.otp, request.new_password)
