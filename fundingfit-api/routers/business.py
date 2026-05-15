from fastapi import APIRouter, Depends, HTTPException

import database as db
from models.business import BusinessProfile, BusinessProfileUpdate
from services.identity_service import require_user

router = APIRouter()


@router.get("/business/me", response_model=BusinessProfile)
async def get_my_business(user: dict = Depends(require_user)):
    profile = db.get_business_profile(user["profile_id"])
    if not profile:
        raise HTTPException(status_code=404, detail="No business profile found")
    return BusinessProfile(**profile)


@router.patch("/business/me", response_model=BusinessProfile)
async def update_my_business(
    update: BusinessProfileUpdate,
    user: dict = Depends(require_user),
):
    """Update manually-provided fields (goals, revenue, headcount)."""
    profile = db.get_business_profile(user["profile_id"])
    if not profile:
        raise HTTPException(status_code=404, detail="No business profile found")

    for field in ("employee_count", "annual_revenue", "goals",
                  "owner_age", "has_rd_activity", "funding_needed"):
        val = getattr(update, field)
        if val is not None:
            profile[field] = val

    db.upsert_business_profile(user["profile_id"], profile)
    return BusinessProfile(**profile)
