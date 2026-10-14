"""Shared dependencies for API routers (avoids circular imports from main.py)."""

import json
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session, joinedload
from jose import JWTError, jwt
from database import get_db
import models
import auth

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).options(joinedload(models.User.role)).filter(models.User.nik == username).first()
    if user is None:
        raise credentials_exception
    return user


def check_user_perm(user: models.User, required_token: str) -> bool:
    """
    Check if user has granular CRUD permission or legacy module permission.
    e.g. check_user_perm(user, "internal.dokumen:delete")
    """
    if not user:
        return False
    if not user.role:
        return False
    if user.role.code == "superadmin":
        return True

    try:
        perms = json.loads(user.role.permissions or "[]")
        if not isinstance(perms, list):
            perms = []
    except Exception:
        perms = []

    if "*" in perms:
        return True
    if required_token in perms:
        return True

    parts = required_token.split(":")
    feature_key = parts[0]
    action = parts[1] if len(parts) > 1 else ""

    if f"{feature_key}:*" in perms:
        return True
    if feature_key in perms:
        return True

    parent_module = feature_key.split(".")[0]
    if parent_module in perms and action == "read":
        return True

    return False


def require_permission(required_token: str):
    """Dependency factory that checks user permission."""
    async def _perm_checker(current_user: models.User = Depends(get_current_user)):
        if not check_user_perm(current_user, required_token):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Akses ditolak: Anda tidak memiliki izin '{required_token}'."
            )
        return current_user
    return _perm_checker
