"""
FastAPI dependency that resolves an X-Session-ID header to a user session.

The session ID is a profile_id from data/companies.json (e.g. "profile-northlight-001").
Sessions are created lazily on first use — no registration step required.
"""

from fastapi import Header, HTTPException

import database as db
from services.companies_house_service import list_profile_ids, lookup_company


def require_user(x_session_id: str = Header(...)) -> dict:
    """
    Looks up the profile_id in companies.json, creates a session if needed,
    and returns the session row. Raises 401 if the profile_id is not recognised.
    """
    profile = lookup_company(x_session_id)
    if not profile:
        raise HTTPException(
            status_code=401,
            detail=f"Unknown profile ID. Available IDs: {list_profile_ids()}",
        )
    db.upsert_session(x_session_id, profile)
    return db.get_session(x_session_id)


def optional_user(x_session_id: str = Header(default=None)) -> dict | None:
    """Returns the session row or None — no error if header is absent or unrecognised."""
    if not x_session_id:
        return None
    profile = lookup_company(x_session_id)
    if not profile:
        return None
    db.upsert_session(x_session_id, profile)
    return db.get_session(x_session_id)
