from typing import Optional

import database as db
from fastapi import APIRouter, Depends, HTTPException
from models.business import BusinessProfile
from models.scheme import SchemeDetail, SchemeSummary
from services.claude_service import translate_scheme
from services.identity_service import optional_user
from services.schemes_service import get_scheme_by_id, load_schemes

router = APIRouter()


@router.get("/schemes", response_model=list[SchemeSummary])
async def list_schemes():
    """All available funding schemes — lightweight list, no Claude call."""
    return [
        SchemeSummary(
            scheme_id=s["id"],
            name=s["name"],
            funder=s["funder"],
            region=s["region"],
            amount_display=s["amount_display"],
            effort_hours=s["effort_hours"],
            source_url=s["source_url"],
        )
        for s in load_schemes()
    ]


@router.get("/schemes/{scheme_id}", response_model=SchemeDetail)
async def get_scheme(
    scheme_id: str,
    user: Optional[dict] = Depends(optional_user),
):
    """
    Full detail for a specific grant scheme with a plain-English summary from Claude.
    If an X-Session-ID header is present the summary is personalised to the user's profile.
    """
    scheme = get_scheme_by_id(scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail=f"Scheme '{scheme_id}' not found")

    business = None
    if user:
        profile_data = db.get_business_profile(user["companies_house_id"])
        if profile_data:
            business = BusinessProfile(**profile_data)

    summary = await translate_scheme(scheme, business)

    return SchemeDetail(
        scheme_id=scheme["id"],
        name=scheme["name"],
        funder=scheme["funder"],
        region=scheme["region"],
        amount_display=scheme["amount_display"],
        max_amount=scheme.get("max_amount"),
        effort_hours=scheme["effort_hours"],
        source_url=scheme["source_url"],
        last_synced=scheme.get("last_synced"),
        eligibility=scheme.get("eligibility", {}),
        plain_english_summary=summary,
    )
