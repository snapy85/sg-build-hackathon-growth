from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

import database as db
from models.business import AmbitionsProfile, BusinessProfile
from services.claude_service import extract_goals
from services.identity_service import require_user

router = APIRouter()


class ExtractRequest(BaseModel):
    free_text: str


class ConfirmRequest(BaseModel):
    expected_growth: str
    opportunity: str
    new_customers: str


@router.post("/goals/extract", response_model=AmbitionsProfile)
async def extract_ambitions(
    request: ExtractRequest,
    user: dict = Depends(require_user),
):
    """
    Screen 04 — Ambitions Question.

    Takes the user's free text input ("What are you looking for support with?")
    and calls Claude to return a structured summary with three fields:
    expected_growth, opportunity, new_customers.

    Does NOT save to the profile yet — the user reviews the summary on
    Screen 06 before confirming. Call /goals/confirm to save.

    Example request:
        { "free_text": "I want to double my revenue and hire 3 people in the next year" }

    Example response:
        {
            "expected_growth": "Double revenue in 12 months",
            "opportunity": "Expand team capacity with new hires",
            "new_customers": "Grow recurring client base by 3 staff hires"
        }
    """
    if not request.free_text or len(request.free_text.strip()) < 5:
        raise HTTPException(
            status_code=400,
            detail="Please enter at least a few words about your ambitions.",
        )

    ambitions = await extract_goals(request.free_text)
    return ambitions


@router.post("/goals/confirm", response_model=BusinessProfile)
async def confirm_ambitions(
    request: ConfirmRequest,
    user: dict = Depends(require_user),
):
    """
    Screen 06 — Review Ambitions.

    User has reviewed (and optionally edited) the structured summary.
    Saves the three ambition fields to the BusinessProfile as a goals list,
    then returns the updated profile.

    After this call the frontend should immediately fire POST /api/match —
    the goals will be present in the profile and generate_fit_signals()
    will use them automatically for matching.

    Example request:
        {
            "expected_growth": "Double revenue in 12 months",
            "opportunity": "AI-led efficiencies",
            "new_customers": "20 new recurring clients"
        }
    """
    profile_id = user["profile_id"]
    profile = db.get_business_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="No business profile found.")

    # Store all three fields as a goals list so generate_fit_signals()
    # receives rich context without needing any changes to the match pipeline
    profile["goals"] = [
        request.expected_growth,
        request.opportunity,
        request.new_customers,
    ]

    db.upsert_business_profile(profile_id, profile)
    return BusinessProfile(**profile)
