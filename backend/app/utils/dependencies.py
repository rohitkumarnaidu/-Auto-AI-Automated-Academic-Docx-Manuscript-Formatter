from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.auth_service import AuthService
from app.schemas.user import User
from typing import Optional
import logging
import jwt

# Set up logging for authentication monitoring
logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False) # Disable auto_error to handle fallback manually

def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> User:
    """
    FastAPI dependency to extract and verify the user from either:
    1. Authorization Bearer header (Preferred)
    2. 'token' query parameter (Fallback for SSE/EventSource)
    """
    token = None
    if credentials:
        token = credentials.credentials
    else:
        # Fallback to query parameter for EventSource compatibility
        token = request.query_params.get("token")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = AuthService.decode_token(token)
        user_id = AuthService.get_user_id_from_payload(payload)
        
        email = payload.get("email")
        role = payload.get("role", "authenticated")
        app_metadata = payload.get("app_metadata")

        try:
            from app.middleware.prometheus_metrics import MetricsManager
            MetricsManager.record_user_activity(str(user_id))
        except Exception:
            pass

        return User(id=user_id, email=email, role=role, app_metadata=app_metadata)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, HTTPException) as e:
        logger.warning(f"Authentication failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_optional_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[User]:
    """
    FastAPI dependency that returns a User if a valid token is present 
    (in header or query param), otherwise returns None.
    """
    token = None
    if credentials:
        token = credentials.credentials
    else:
        token = request.query_params.get("token")
        
    if not token:
        return None
        
    try:
        payload = AuthService.decode_token(token)
        user_id = AuthService.get_user_id_from_payload(payload)
        email = payload.get("email")
        role = payload.get("role", "authenticated")
        app_metadata = payload.get("app_metadata")
        try:
            from app.middleware.prometheus_metrics import MetricsManager
            MetricsManager.record_user_activity(str(user_id))
        except Exception:
            pass
        return User(id=user_id, email=email, role=role, app_metadata=app_metadata)
    except Exception as e:
        logger.warning(f"Optional token validation failed: {str(e)}")
        return None


def _has_admin_scope(user: User) -> bool:
    role = str(getattr(user, "role", "") or "").strip().lower()
    if role in {"admin", "service_role"}:
        return True

    app_metadata = getattr(user, "app_metadata", None)
    if not isinstance(app_metadata, dict):
        return False

    metadata_role = app_metadata.get("role")
    if isinstance(metadata_role, str) and metadata_role.strip().lower() == "admin":
        return True

    metadata_roles = app_metadata.get("roles")
    if isinstance(metadata_roles, str):
        return metadata_roles.strip().lower() == "admin"
    if isinstance(metadata_roles, list):
        normalized = {str(item).strip().lower() for item in metadata_roles}
        return "admin" in normalized

    return False


def require_admin_user(user: User = Depends(get_current_user)) -> User:
    if not _has_admin_scope(user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user
