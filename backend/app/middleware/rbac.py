from __future__ import annotations

from fastapi import Depends, HTTPException, status

from app.utils.dependencies import get_current_user


def require_role(role: str):
    def _guard(current_user=Depends(get_current_user)):
        role_value = getattr(current_user, "role", None)
        meta_role = None
        app_metadata = getattr(current_user, "app_metadata", None)
        if isinstance(app_metadata, dict):
            meta_role = app_metadata.get("role")
        if role_value == role or meta_role == role:
            return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    return _guard
