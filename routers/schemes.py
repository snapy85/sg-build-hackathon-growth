from typing import Optional

import database as db
from fastapi import APIRouter, Depends, HTTPException
from models.business import BusinessProfile
from models.scheme import SchemeDetail, SchemeSummary
from services.claude_service import translate_scheme
from services.identity_service import optional_user
from services.schemes_service import get_scheme_by_id, load_schemes

# How GET /api/schemes/{scheme_id} works:
#
# 1. get_scheme_by_id() opens data/schemes.json and scans for a scheme whose
#    "id" field matches the path parameter. Returns the raw dict or None.
#
# 2. If no X-Session-ID header is present (user is anonymous), the scheme's
#    own "summary" field is returned as-is — no Claude call, no API key needed.
#
# 3. If an X-Session-ID header IS present, the user's business profile is
#    loaded from SQLite and passed to Claude's translate_scheme() function,
#    which rewrites the summary personalised to that specific business.

router = APIRouter()


@router.get("/schemes", response_model=list[SchemeSummary])
async def list_schemes():
    """All available funding schemes — lightweight list, no Claude call."""
    return [
        SchemeSummary(
            scheme_id=s["id"],
            name=s["name"],
            provider=s["provider"],
            type=s["type"],
            repayable=s["repayable"],
            funding_display=s["funding"]["display"],
            effort_display=s["effort"]["display"],
            url=s["url"],
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

    if user:
        # Session present — load profile and ask Claude for a personalised summary
        profile_data = db.get_business_profile(user["companies_house_id"])
        business = BusinessProfile(**profile_data) if profile_data else None
        plain_english_summary = await translate_scheme(scheme, business)
    else:
        # No session — return the scheme's own summary directly from schemes.json
        plain_english_summary = scheme["summary"]

    return SchemeDetail(
        scheme_id=scheme["id"],
        name=scheme["name"],
        provider=scheme["provider"],
        url=scheme["url"],
        type=scheme["type"],
        repayable=scheme["repayable"],
        funding=scheme["funding"],
        summary=scheme["summary"],
        eligibility=scheme["eligibility"],
        documents=scheme.get("documents", []),
        restrictions=scheme.get("restrictions", []),
        effort=scheme["effort"],
        timeline=scheme["timeline"],
        last_verified=scheme.get("last_verified"),
        plain_english_summary=plain_english_summary,
    )
