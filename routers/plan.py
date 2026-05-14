from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

import database as db
from models.business import BusinessProfile
from models.scheme import PlanItem, PlanResponse
from services.claude_service import generate_plan
from services.identity_service import optional_user
from services.schemes_service import get_scheme_by_id

router = APIRouter()


class PlanRequest(BaseModel):
    scheme_ids: List[str]


_MOCK_PLAN = PlanResponse(
    shared_requirements=[
        "Last 6 months bank statements",
        "A short description of your business (150 words)",
        "Proof of trading address",
        "Most recent annual revenue figure",
    ],
    schemes=[
        PlanItem(
            scheme_id="adventure-grant",
            name="AD:VENTURE Grant",
            shared_requirements=[
                "Last 6 months bank statements",
                "A short description of your business (150 words)",
                "Proof of trading address",
            ],
            scheme_specific_requirements=[
                "Evidence of West Yorkshire location (e.g. utility bill or lease)",
                "Description of how the grant funds will be used",
            ],
        ),
        PlanItem(
            scheme_id="wy-growth-fund",
            name="WY Growth Fund",
            shared_requirements=[
                "Last 6 months bank statements",
                "A short description of your business (150 words)",
                "Most recent annual revenue figure",
            ],
            scheme_specific_requirements=[
                "12-month financial projections",
                "Written scaling plan (500 words)",
            ],
        ),
        PlanItem(
            scheme_id="startup-loan",
            name="Start Up Loan",
            shared_requirements=[
                "Last 6 months bank statements",
                "Most recent annual revenue figure",
            ],
            scheme_specific_requirements=[
                "Personal credit check consent",
                "Personal identification (passport or driving licence)",
                "Business plan",
            ],
        ),
    ],
)


@router.post("/plan", response_model=PlanResponse)
async def create_plan(
    request: PlanRequest,
    mock: bool = False,
    user: Optional[dict] = Depends(optional_user),
):
    if mock:
        return _MOCK_PLAN

    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    selected_schemes = []
    for sid in request.scheme_ids:
        scheme = get_scheme_by_id(sid)
        if scheme is None:
            raise HTTPException(status_code=404, detail=f"Scheme '{sid}' not found")
        selected_schemes.append(scheme)

    ch_id = user["profile_id"]
    profile_data = db.get_business_profile(ch_id)
    business = BusinessProfile(**profile_data) if profile_data else None

    result = await generate_plan(selected_schemes, business)

    db.save_interaction(
        ch_id,
        "plan",
        {"scheme_ids": request.scheme_ids},
        result.model_dump(),
    )

    return result
