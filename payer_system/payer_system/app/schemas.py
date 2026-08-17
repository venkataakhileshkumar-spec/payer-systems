"""
Pydantic schemas: define the shape of data going in/out of the API.
Kept separate from the SQLAlchemy models (app/models.py) on purpose,
so the API contract can evolve independently of the DB schema.
"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models import ClaimStatus


# ---------- Member ----------

class MemberBase(BaseModel):
    member_number: str
    first_name: str
    last_name: str
    date_of_birth: date
    plan_name: str = "Standard"
    is_active: bool = True


class MemberCreate(MemberBase):
    pass


class MemberUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    plan_name: Optional[str] = None
    is_active: Optional[bool] = None


class MemberOut(MemberBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


# ---------- Provider ----------

class ProviderBase(BaseModel):
    npi: str
    name: str
    specialty: Optional[str] = None
    is_in_network: bool = True


class ProviderCreate(ProviderBase):
    pass


class ProviderUpdate(BaseModel):
    name: Optional[str] = None
    specialty: Optional[str] = None
    is_in_network: Optional[bool] = None


class ProviderOut(ProviderBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


# ---------- Claim ----------

class ClaimBase(BaseModel):
    claim_number: str
    member_id: int
    provider_id: int
    service_date: date
    diagnosis_code: Optional[str] = None
    procedure_code: Optional[str] = None
    billed_amount: float


class ClaimCreate(ClaimBase):
    pass


class ClaimUpdate(BaseModel):
    status: Optional[ClaimStatus] = None
    allowed_amount: Optional[float] = None
    paid_amount: Optional[float] = None
    notes: Optional[str] = None


class ClaimOut(ClaimBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    status: ClaimStatus
    allowed_amount: Optional[float] = None
    paid_amount: Optional[float] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
