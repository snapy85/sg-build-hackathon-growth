from typing import List, Optional

from pydantic import BaseModel


class BusinessProfile(BaseModel):
    business_name: str
    trading_status: str          # sole_trader | limited_company | partnership
    registration_date: str
    sector: str
    postcode: str
    employee_count: Optional[int] = None
    annual_revenue: Optional[float] = None
    goals: List[str] = []
    data_sources: List[str] = []
    companies_house_id: Optional[str] = None
    # Collected during onboarding for scheme-specific gates
    owner_age: Optional[int] = None
    has_rd_activity: Optional[bool] = None
    funding_needed: Optional[int] = None


class BusinessProfileUpdate(BaseModel):
    """Fields a user can manually update after the CH/HMRC import."""
    employee_count: Optional[int] = None
    annual_revenue: Optional[float] = None
    goals: Optional[List[str]] = None
    owner_age: Optional[int] = None
    has_rd_activity: Optional[bool] = None
    funding_needed: Optional[int] = None
