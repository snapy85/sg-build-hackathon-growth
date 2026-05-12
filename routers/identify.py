import json
from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import database as db
from models.business import BusinessProfile
from routers.history import _summarise
from services.companies_house_service import list_mock_ids, lookup_company

router = APIRouter()


class IdentifyRequest(BaseModel):
    companies_house_id: str


class IdentifyResponse(BaseModel):
    session_id: str
    profile: BusinessProfile
    is_returning: bool
    last_match: Optional[dict[str, Any]] = None


@router.post("/identify", response_model=IdentifyResponse)
async def identify(req: IdentifyRequest):
    """
    Enter a Companies House ID to start or resume a session.

    - First visit: creates a session and returns is_returning=false, last_match=null
    - Returning visit: refreshes last_seen, returns is_returning=true and the
      summary of the most recent match (if one exists) so the frontend can
      show "welcome back — you matched X grants last time."

    The returned session_id (same as the CH ID) must be sent as the
    X-Session-ID header on all subsequent authenticated requests.
    """
    company = lookup_company(req.companies_house_id)
    if not company:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Companies House ID '{req.companies_house_id}' not recognised. "
                f"Available demo IDs: {list_mock_ids()}"
            ),
        )

    is_returning = db.upsert_session(req.companies_house_id, company)

    last_match = None
    if is_returning:
        history = db.get_history(req.companies_house_id)
        for row in history:
            if row["action"] == "match":
                last_match = _summarise("match", json.loads(row["output_data"]))
                break

    profile_data = db.get_business_profile(req.companies_house_id) or company

    return IdentifyResponse(
        session_id=req.companies_house_id,
        profile=BusinessProfile(**profile_data),
        is_returning=is_returning,
        last_match=last_match,
    )
