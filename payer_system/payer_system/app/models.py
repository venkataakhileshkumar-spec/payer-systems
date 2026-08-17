"""
Core domain models for the Payer System.

A "payer" (health insurer) tracks:
- Members: the insured individuals
- Providers: doctors/clinics/hospitals who deliver care
- Claims: requests for payment submitted by providers on behalf of members
"""

import enum
from datetime import date, datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Date,
    DateTime,
    ForeignKey,
    Enum as SAEnum,
    Text,
)
from sqlalchemy.orm import relationship

from app.database import Base


class ClaimStatus(str, enum.Enum):
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    PAID = "PAID"


class Member(Base):
    """An insured individual (policyholder or dependent)."""

    __tablename__ = "members"

    id = Column(Integer, primary_key=True, index=True)
    member_number = Column(String(32), unique=True, index=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    plan_name = Column(String(100), nullable=False, default="Standard")
    is_active = Column(Integer, default=1)  # 1 = active, 0 = inactive
    created_at = Column(DateTime, default=datetime.utcnow)

    claims = relationship("Claim", back_populates="member", cascade="all, delete-orphan")


class Provider(Base):
    """A doctor, clinic, or facility that submits claims for services rendered."""

    __tablename__ = "providers"

    id = Column(Integer, primary_key=True, index=True)
    npi = Column(String(20), unique=True, index=True, nullable=False)  # National Provider Identifier
    name = Column(String(150), nullable=False)
    specialty = Column(String(100), nullable=True)
    is_in_network = Column(Integer, default=1)  # 1 = in-network, 0 = out-of-network
    created_at = Column(DateTime, default=datetime.utcnow)

    claims = relationship("Claim", back_populates="provider", cascade="all, delete-orphan")


class Claim(Base):
    """A request for payment submitted by a provider for services given to a member."""

    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)
    claim_number = Column(String(32), unique=True, index=True, nullable=False)

    member_id = Column(Integer, ForeignKey("members.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)

    service_date = Column(Date, nullable=False)
    diagnosis_code = Column(String(20), nullable=True)   # e.g. ICD-10 code
    procedure_code = Column(String(20), nullable=True)   # e.g. CPT code
    billed_amount = Column(Float, nullable=False)
    allowed_amount = Column(Float, nullable=True)   # set during adjudication
    paid_amount = Column(Float, nullable=True)       # set once paid

    status = Column(SAEnum(ClaimStatus), default=ClaimStatus.SUBMITTED, nullable=False)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    member = relationship("Member", back_populates="claims")
    provider = relationship("Provider", back_populates="claims")
