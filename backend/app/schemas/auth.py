from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional

class SignupRequest(BaseModel):
    full_name: str = Field(..., min_length=1)
    email: EmailStr
    institution: Optional[str] = None
    password: str = Field(..., min_length=8)
    terms_accepted: bool = Field(...)

    @field_validator('terms_accepted')
    @classmethod
    def must_be_true(cls, v):
        if v is not True:
            raise ValueError('Terms and conditions must be accepted')
        return v

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=8)
