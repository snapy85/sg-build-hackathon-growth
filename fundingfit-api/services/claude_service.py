import json
import logging
import os
from typing import Optional

from anthropic import AsyncAnthropic
from dotenv import load_dotenv
from fastapi import HTTPException

from models.business import BusinessProfile
from models.scheme import PlanItem, PlanResponse, SchemeResult

load_dotenv()

logger = logging.getLogger(__name__)

MODEL = "claude-sonnet-4-0"
MAX_TOKENS = 1000

_client: Optional[AsyncAnthropic] = None


def _get_client() -> AsyncAnthropic:
    global _client
    if _client is None:
        _client = AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    return _client


_FIT_SIGNALS_SYSTEM = (
    "You are a UK small business funding advisor. "
    "You will be given a business profile and a list of funding schemes with eligibility rules. "
    "For each scheme, first assess hard eligibility (trading age, region, employee count, trading status). "
    "Then consider the business's stated goals: if a goal directly matches what the scheme funds "
    "(e.g. goal is 'buy equipment' and the scheme covers equipment costs), "
    "this should tip a borderline case from 'possible' to 'strong_match'. "
    "Reply ONLY with a valid JSON array. No preamble, no markdown, no explanation outside the JSON.\n\n"
    "Each object in the array must have exactly these keys:\n"
    "scheme_id, fit (strong_match | possible | not_suitable), "
    "fit_reason (one plain-English sentence referencing the actual eligibility and, where relevant, how it aligns with the business's goals), "
    "plain_english_summary (2 sentences: who it is for, what it funds), "
    "eligibility_met (list of criteria the business meets), "
    "eligibility_unmet (list of criteria the business does not meet or where it is unclear)"
)

_TRANSLATE_SYSTEM = (
    "Rewrite this grant scheme description in plain English for a small business owner "
    "with no finance background. Two sentences maximum: first sentence says who it is "
    "really for and what it funds. Second sentence says the one most important thing "
    "to know before applying. No jargon."
)

_PLAN_SYSTEM = (
    "You are helping a small business owner prepare applications for multiple funding schemes. "
    "Given the selected schemes and their requirements, identify which documents or pieces of "
    "information appear in more than one application. "
    "Reply ONLY with valid JSON — no preamble, no markdown.\n\n"
    "Return an object with:\n"
    "- shared_requirements: list of strings (items needed for 2+ schemes, plain English, "
    "e.g. 'Last 6 months bank statements', 'A short description of your business (150 words)')\n"
    "- schemes: array of objects, each with scheme_id, name, "
    "and scheme_specific_requirements (list of strings, items only needed for that scheme)"
)

# --- NEW: Goals extraction system prompt ---
_EXTRACT_GOALS_SYSTEM = (
    "You are helping a UK small business owner articulate their ambitions. "
    "Given their free text description, extract exactly three fields. "
    "Reply ONLY with a valid JSON object — no preamble, no markdown.\n\n"
    "Fields:\n"
    "- expected_growth: one concise sentence describing their growth target "
    "(e.g. 'Double revenue in 12 months')\n"
    "- opportunity: one concise sentence describing how they plan to achieve it "
    "(e.g. 'AI-led efficiencies')\n"
    "- new_customers: one concise sentence describing their customer goal "
    "(e.g. '20 new recurring clients')\n\n"
    "If the user does not mention one of these, make a reasonable inference "
    "from what they did say. Keep each field under 10 words."
)


async def generate_fit_signals(
    business: BusinessProfile, schemes: list[dict]
) -> list[SchemeResult]:
    client = _get_client()
    raw_response = ""
    try:
        response = await client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=[
                {
                    "type": "text",
                    "text": _FIT_SIGNALS_SYSTEM,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"Business profile:\n{json.dumps(business.model_dump(), indent=2)}\n\n"
                        f"Schemes:\n{json.dumps(schemes, indent=2)}"
                    ),
                }
            ],
        )

        raw_response = next(
            (b.text for b in response.content if b.type == "text"), ""
        )
        fit_data = json.loads(raw_response)

        from services.schemes_service import infer_region
        scheme_map = {s["id"]: s for s in schemes}
        results = []
        for item in fit_data:
            sid = item["scheme_id"]
            scheme = scheme_map.get(sid, {})
            results.append(
                SchemeResult(
                    scheme_id=sid,
                    name=scheme.get("name", ""),
                    provider=scheme.get("provider", ""),
                    region=infer_region(scheme),
                    funding_display=scheme.get("funding", {}).get("display", ""),
                    effort_hours=scheme.get("effort", {}).get("hours", 0),
                    fit=item["fit"],
                    fit_reason=item["fit_reason"],
                    plain_english_summary=item["plain_english_summary"],
                    eligibility_met=item.get("eligibility_met", []),
                    eligibility_unmet=item.get("eligibility_unmet", []),
                    url=scheme.get("url", ""),
                )
            )
        return results

    except json.JSONDecodeError:
        logger.error("Claude returned malformed JSON for fit_signals: %s", raw_response)
        raise HTTPException(
            status_code=502,
            detail="AI service returned an unexpected response",
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Claude API error in generate_fit_signals: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="AI service returned an unexpected response",
        )


async def translate_scheme(scheme: dict, business: Optional[BusinessProfile] = None) -> str:
    client = _get_client()
    try:
        user_content = f"Scheme:\n{json.dumps(scheme, indent=2)}"
        if business:
            user_content += f"\n\nBusiness:\n{json.dumps(business.model_dump(), indent=2)}"

        response = await client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=[
                {
                    "type": "text",
                    "text": _TRANSLATE_SYSTEM,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": user_content}],
        )
        return next((b.text for b in response.content if b.type == "text"), "")

    except Exception as exc:
        logger.error("Claude API error in translate_scheme: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="AI service returned an unexpected response",
        )


async def generate_plan(
    selected_schemes: list[dict],
    business: Optional[BusinessProfile] = None,
) -> PlanResponse:
    client = _get_client()
    raw_response = ""
    try:
        user_content = f"Selected schemes:\n{json.dumps(selected_schemes, indent=2)}"
        if business:
            user_content += (
                f"\n\nBusiness profile:\n{json.dumps(business.model_dump(), indent=2)}"
            )

        response = await client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=[
                {
                    "type": "text",
                    "text": _PLAN_SYSTEM,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": user_content}],
        )

        raw_response = next(
            (b.text for b in response.content if b.type == "text"), ""
        )
        plan_data = json.loads(raw_response)

        scheme_items = [
            PlanItem(
                scheme_id=s["scheme_id"],
                name=s["name"],
                shared_requirements=[],
                scheme_specific_requirements=s.get("scheme_specific_requirements", []),
            )
            for s in plan_data.get("schemes", [])
        ]

        return PlanResponse(
            shared_requirements=plan_data.get("shared_requirements", []),
            schemes=scheme_items,
        )

    except json.JSONDecodeError:
        logger.error("Claude returned malformed JSON for generate_plan: %s", raw_response)
        raise HTTPException(
            status_code=502,
            detail="AI service returned an unexpected response",
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Claude API error in generate_plan: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="AI service returned an unexpected response",
        )


# --- NEW: Goals extraction function ---
async def extract_goals(free_text: str):
    """Converts free text ambitions into a structured AmbitionsProfile.
    Called by POST /api/goals/extract before saving to the business profile.
    """
    from models.business import AmbitionsProfile
    client = _get_client()
    raw_response = ""
    try:
        response = await client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=[
                {
                    "type": "text",
                    "text": _EXTRACT_GOALS_SYSTEM,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": f"Business owner's ambitions:\n{free_text}",
                }
            ],
        )

        raw_response = next(
            (b.text for b in response.content if b.type == "text"), ""
        )
        goals_data = json.loads(raw_response)
        return AmbitionsProfile(**goals_data)

    except json.JSONDecodeError:
        logger.error("Claude returned malformed JSON for extract_goals: %s", raw_response)
        raise HTTPException(
            status_code=502,
            detail="AI service returned an unexpected response",
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Claude API error in extract_goals: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="AI service returned an unexpected response",
        )
