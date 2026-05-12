from fastapi import APIRouter, Depends, HTTPException

import database as db
from models.business import BusinessProfile, BusinessProfileUpdate
from services.identity_service import require_user

router = APIRouter()


@router.get("/business/me", response_model=BusinessProfile)
async def get_my_business(user: dict = Depends(require_user)):
    profile = db.get_business_profile(user["companies_house_id"])
    if not profile:
        raise HTTPException(status_code=404, detail="No business profile found")
    return BusinessProfile(**profile)


@router.patch("/business/me", response_model=BusinessProfile)
async def update_my_business(
    update: BusinessProfileUpdate,
    user: dict = Depends(require_user),
):
    """Update manually-provided fields (goals, revenue, headcount)."""
    profile = db.get_business_profile(user["companies_house_id"])
    if not profile:
        raise HTTPException(status_code=404, detail="No business profile found")

    if update.employee_count is not None:
        profile["employee_count"] = update.employee_count
    if update.annual_revenue is not None:
        profile["annual_revenue"] = update.annual_revenue
    if update.goals is not None:
        profile["goals"] = update.goals

    db.upsert_business_profile(user["companies_house_id"], profile)
    return BusinessProfile(**profile)
