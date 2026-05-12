from typing import Any, List, Optional

from pydantic import BaseModel


class SchemeSummary(BaseModel):
    scheme_id: str
    name: str
    funder: str
    region: str
    amount_display: str
    effort_hours: int
    source_url: str


class SchemeDetail(BaseModel):
    scheme_id: str
    name: str
    funder: str
    region: str
    amount_display: str
    max_amount: Optional[int] = None
    effort_hours: int
    source_url: str
    last_synced: Optional[str] = None
    eligibility: dict[str, Any]
    plain_english_summary: str


class SchemeResult(BaseModel):
    scheme_id: str
    name: str
    funder: str
    region: str
    amount_display: str
    effort_hours: int
    fit: str  # strong_match | possible | not_suitable
    fit_reason: str
    plain_english_summary: str
    eligibility_met: List[str]
    eligibility_unmet: List[str]
    source_url: str


class PlanItem(BaseModel):
    scheme_id: str
    name: str
    shared_requirements: List[str]
    scheme_specific_requirements: List[str]


class PlanResponse(BaseModel):
    shared_requirements: List[str]
    schemes: List[PlanItem]
