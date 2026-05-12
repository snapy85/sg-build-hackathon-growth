"""
Mock Companies House + HMRC lookup service.

In production this would call:
  - GET https://api.company-information.service.gov.uk/company/{number}
  - HMRC Making Tax Digital API (OAuth 2.0) for revenue and PAYE data

For the hackathon we resolve the company number against data/mock_companies.json,
which is pre-populated with realistic profiles as if both APIs had already responded.
"""

import json
import os
from typing import Optional

_MOCK_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "mock_companies.json")
_cache: dict | None = None


def _load_mock() -> dict:
    global _cache
    if _cache is None:
        with open(_MOCK_PATH) as f:
            _cache = json.load(f)
    return _cache


def lookup_company(companies_house_id: str) -> Optional[dict]:
    """
    Return the enriched business profile for a given Companies House ID,
    or None if not found.

    The returned dict matches the BusinessProfile schema so it can be
    stored directly and returned to the client.
    """
    return _load_mock().get(companies_house_id.upper()) or _load_mock().get(companies_house_id)


def list_mock_ids() -> list[str]:
    """Helper used in tests / docs to show which IDs are available."""
    return list(_load_mock().keys())
