"""
FastAPI dependency that resolves an X-Session-ID header to a session dict.
The session ID is the Companies House ID — no tokens or passwords needed.
"""

from fastapi import Depends, Header, HTTPException

import database as db


def require_user(x_session_id: str = Header(...)) -> dict:
    """Raises 401 if the header is missing or unknown. Returns the session row."""
    session = db.get_session(x_session_id)
    if not session:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing X-Session-ID header. Call POST /api/identify first.",
        )
    return session


def optional_user(x_session_id: str = Header(default=None)) -> dict | None:
    """Returns the session row or None — no error if unauthenticated."""
    if not x_session_id:
        return None
    return db.get_session(x_session_id)
