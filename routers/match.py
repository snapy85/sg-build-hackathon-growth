from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException

import database as db
from models.business import BusinessProfile
from models.scheme import SchemeResult
from services.claude_service import generate_fit_signals
from services.identity_service import optional_user
from services.schemes_service import filter_by_region, load_schemes

router = APIRouter()

_FIT_ORDER = {"strong_match": 0, "possible": 1, "not_suitable": 2}
_REGION_ORDER = {"leeds": 0, "west_yorkshire": 0, "national": 1}

_MOCK_RESULTS: List[SchemeResult] = [
    SchemeResult(
        scheme_id="adventure-grant",
        name="AD:VENTURE Grant",
        funder="West Yorkshire Combined Authority",
        region="west_yorkshire",
        amount_display="Up to £5,000",
        effort_hours=2,
        fit="strong_match",
        fit_reason="Trading under 3 years in West Yorkshire in an eligible creative sector.",
        plain_english_summary=(
            "A grant for early-stage businesses in West Yorkshire's creative, digital, "
            "and professional services sectors. It can fund equipment, marketing, and "
            "other growth costs up to £5,000."
        ),
        eligibility_met=["Based in West Yorkshire", "Trading under 3 years", "Eligible sector (creative services)"],
        eligibility_unmet=[],
        source_url="https://ad-venture.org.uk",
    ),
    SchemeResult(
        scheme_id="wy-growth-fund",
        name="WY Growth Fund",
        funder="West Yorkshire Combined Authority",
        region="west_yorkshire",
        amount_display="Up to £25,000",
        effort_hours=4,
        fit="possible",
        fit_reason="Based in West Yorkshire and trading over 1 year, but a scaling plan and financial projections will need to be demonstrated.",
        plain_english_summary=(
            "A larger grant for West Yorkshire businesses that are ready to grow. "
            "You will need a clear written growth plan and 12-month financial projections to apply."
        ),
        eligibility_met=["Based in West Yorkshire", "Trading over 1 year"],
        eligibility_unmet=["Scaling plan required", "Financial projections required"],
        source_url="https://westyorks-ca.gov.uk/business/",
    ),
    SchemeResult(
        scheme_id="startup-loan",
        name="Start Up Loan",
        funder="British Business Bank",
        region="national",
        amount_display="£500–£25,000",
        effort_hours=3,
        fit="strong_match",
        fit_reason="UK-based and trading under 2 years, meeting the core eligibility criteria.",
        plain_english_summary=(
            "A government-backed personal loan for new UK businesses trading under two years. "
            "The most important thing to know is that it involves a personal credit check."
        ),
        eligibility_met=["UK-based", "Trading under 2 years"],
        eligibility_unmet=["Personal credit check required"],
        source_url="https://startuploans.co.uk",
    ),
    SchemeResult(
        scheme_id="leeds-council-grant",
        name="Leeds City Council Business Support Grant",
        funder="Leeds City Council",
        region="leeds",
        amount_display="Up to £2,500",
        effort_hours=2,
        fit="strong_match",
        fit_reason="Based in Leeds, trading under 2 years, and has fewer than 10 employees.",
        plain_english_summary=(
            "A small grant for new businesses based in Leeds with fewer than 10 employees. "
            "It covers early-stage costs like equipment or marketing."
        ),
        eligibility_met=["Based in Leeds", "Trading under 2 years", "Under 10 employees"],
        eligibility_unmet=[],
        source_url="https://leeds.gov.uk/business-support-and-advice/helping-your-business-grow",
    ),
    SchemeResult(
        scheme_id="help-to-grow",
        name="Help to Grow: Management",
        funder="Department for Business & Trade",
        region="national",
        amount_display="Subsidised leadership course (£750 government contribution)",
        effort_hours=1,
        fit="not_suitable",
        fit_reason="Requires 5 or more employees; this business currently has 1 employee.",
        plain_english_summary=(
            "A subsidised business leadership course for small business owners with at least 5 staff. "
            "Not available to sole traders or businesses below the 5-employee threshold."
        ),
        eligibility_met=["Trading over 1 year", "Not in public sector"],
        eligibility_unmet=["Requires 5+ employees (currently 1)"],
        source_url="https://helptogrow.campaign.gov.uk",
    ),
    SchemeResult(
        scheme_id="rd-tax-relief",
        name="R&D Tax Relief (HMRC)",
        funder="HMRC",
        region="national",
        amount_display="Up to 33% of qualifying R&D spend reclaimed",
        effort_hours=5,
        fit="not_suitable",
        fit_reason="Only available to limited companies; this business is a sole trader with no indicated qualifying R&D spend.",
        plain_english_summary=(
            "A tax relief scheme for limited companies that spend money on innovation. "
            "Sole traders cannot claim this relief, and an accountant is typically required."
        ),
        eligibility_met=[],
        eligibility_unmet=[
            "Limited company required (business is sole trader)",
            "Qualifying R&D spend required",
            "Accountant involvement required",
        ],
        source_url="https://gov.uk/guidance/corporation-tax-research-and-development-rd-relief",
    ),
]


def _sort_results(results: List[SchemeResult]) -> List[SchemeResult]:
    return sorted(
        results,
        key=lambda r: (_FIT_ORDER.get(r.fit, 99), _REGION_ORDER.get(r.region, 2)),
    )


@router.post("/match", response_model=List[SchemeResult])
async def match_schemes(
    mock: bool = False,
    user: Optional[dict] = Depends(optional_user),
):
    if mock:
        return _sort_results(_MOCK_RESULTS)

    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    ch_id = user["companies_house_id"]
    profile_data = db.get_business_profile(ch_id)
    if not profile_data:
        raise HTTPException(status_code=404, detail="No business profile found. Call /api/identify first.")

    business = BusinessProfile(**profile_data)
    schemes = load_schemes()
    relevant = filter_by_region(schemes, business.postcode)
    results = await generate_fit_signals(business, relevant)
    sorted_results = _sort_results(results)

    db.save_interaction(
        ch_id,
        "match",
        {"companies_house_id": ch_id},
        [r.model_dump() for r in sorted_results],
    )

    return sorted_results
