"""
Mock Companies House + HMRC lookup service.

In production this would call:
  - GET https://api.company-information.service.gov.uk/company/{number}
  - HMRC Making Tax Digital API (OAuth 2.0) for revenue and PAYE data

For the hackathon we resolve the identifier against data/companies.json,
which is pre-populated with realistic profiles as if both APIs had already
responded. Each profile contains nested companies_house and hmrc sections
that mirror real API response shapes.
"""

import json
import os
from typing import Optional

_COMPANIES_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "companies.json")
_cache: list | None = None


def _load_companies() -> list:
    global _cache
    if _cache is None:
        with open(_COMPANIES_PATH) as f:
            _cache = json.load(f)
    return _cache


def _to_business_profile(profile: dict) -> dict:
    """
    Maps the rich companies.json profile shape onto the flat BusinessProfile
    dict that the rest of the app expects.
    """
    ch = profile.get("companies_house") or {}
    hmrc = profile.get("hmrc") or {}
    derived = profile.get("derived") or {}
    user_provided = profile.get("user_provided") or {}

    address = ch.get("registered_office_address") or {}
    paye = hmrc.get("paye") or {}
    sa = hmrc.get("self_assessment") or {}

    # Pull the most recent goals session's extracted intended spend
    goals = []
    goal_sessions = profile.get("goals") or []
    if goal_sessions:
        extracted = goal_sessions[-1].get("extracted") or {}
        goals = extracted.get("intended_spend") or []

    data_sources = []
    if ch:
        data_sources.append("Companies House")
    if hmrc:
        data_sources.append("HMRC")

    return {
        "business_name": user_provided.get("trading_name") or ch.get("legal_name", ""),
        "trading_status": derived.get("legal_structure", ""),
        "registration_date": ch.get("incorporation_date") or sa.get("trading_start_date", ""),
        "sector": derived.get("sector", ""),
        "postcode": address.get("postal_code", ""),
        "employee_count": paye.get("employees_on_payroll"),
        "annual_revenue": sa.get("turnover"),
        "goals": goals,
        "data_sources": data_sources,
        "companies_house_id": ch.get("company_number") or profile.get("profile_id"),
    }


def lookup_company(profile_id: str) -> Optional[dict]:
    """
    Look up a company by profile_id.
    Returns a BusinessProfile-compatible dict or None if not found.
    """
    for profile in _load_companies():
        if profile.get("profile_id") == profile_id:
            return _to_business_profile(profile)
    return None


def list_profile_ids() -> list[str]:
    """Returns all available profile IDs."""
    return [p["profile_id"] for p in _load_companies()]
