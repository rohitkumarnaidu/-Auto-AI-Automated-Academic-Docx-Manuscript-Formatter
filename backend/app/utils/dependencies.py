from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.auth_service import AuthService
from app.schemas.user import User

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """
    FastAPI dependency to extract and verify the user from the Bearer token.
    Uses AuthService for token decoding and validation.
    """
    token = credentials.credentials
    payload = AuthService.decode_token(token)
    user_id = AuthService.get_user_id_from_payload(payload)
    
    # In a full valid flow, we might also check if the user exists in our local DB here
    # For now, we trust the token and construct the User schema directly
    email = payload.get("email")
    role = payload.get("role", "authenticated")

    return User(id=user_id, email=email, role=role)

def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Optional[User]:
    """
    FastAPI dependency that returns a User if a valid token is present, 
    otherwise returns None. Used for anonymous-friendly endpoints.
    """
    if not credentials:
        return None
        
    try:
        token = credentials.credentials
        payload = AuthService.decode_token(token)
        user_id = AuthService.get_user_id_from_payload(payload)
        email = payload.get("email")
        role = payload.get("role", "authenticated")
        return User(id=user_id, email=email, role=role)
    except:
        return None
