"""
HH LOANHUB - Authentication & Security Helpers
"""

import secrets
import time
from typing import Optional
from fastapi import Header, HTTPException, status
from core.database import get_db_connection

# In-memory active session token store (token -> user_id, expires_at)
SESSIONS: dict[str, dict] = {}
SESSION_TTL_SECONDS = 86400 * 30  # 30 days session validity


def create_session_token(user_id: int) -> str:
    """Generates a secure 32-byte hex session token and stores in session cache."""
    token = secrets.token_hex(32)
    SESSIONS[token] = {
        "user_id": user_id,
        "expires_at": time.time() + SESSION_TTL_SECONDS
    }
    return token


def get_current_user_from_token(authorization: Optional[str] = Header(None)) -> dict:
    """Dependency to retrieve the authenticated user from the Authorization header."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header."
        )

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format. Expected 'Bearer <token>'."
        )

    token = parts[1]
    session = SESSIONS.get(token)
    if not session or time.time() > session["expires_at"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid. Please log in again."
        )

    user_id = session["user_id"]
    conn = get_db_connection()
    try:
        user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found."
            )
        return dict(user)
    finally:
        conn.close()


def require_admin(authorization: Optional[str] = Header(None)) -> dict:
    """Dependency that ensures the authenticated user has the 'admin' role."""
    user = get_current_user_from_token(authorization)
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrative privileges required."
        )
    return user
