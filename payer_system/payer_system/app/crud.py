"""
Data-access + business-logic layer.

Kept separate from the routers so the logic (e.g. claim adjudication)
is easy to unit test without spinning up the HTTP layer.
"""

from typing import Optional, List

from sqlalchemy.orm import Session

from app import models, schemas


# ---------- Member ----------

def create_member(db: Session, member: schemas.MemberCreate) -> models.Member:
    db_member = models.Member(**member.model_dump())
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


def get_member(db: Session, member_id: int) -> Optional[models.Member]:
    return db.query(models.Member).filter(models.Member.id == member_id).first()


def get_members(db: Session, skip: int = 0, limit: int = 100) -> List[models.Member]:
    return db.query(models.Member).offset(skip).limit(limit).all()


def update_member(db: Session, member_id: int, updates: schemas.MemberUpdate) -> Optional[models.Member]:
    db_member = get_member(db, member_id)
    if not db_member:
        return None
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(db_member, field, value)
    db.commit()
    db.refresh(db_member)
    return db_member


def delete_member(db: Session, member_id: int) -> bool:
    db_member = get_member(db, member_id)
    if not db_member:
        return False
    db.delete(db_member)
    db.commit()
    return True


# ---------- Provider ----------

def create_provider(db: Session, provider: schemas.ProviderCreate) -> models.Provider:
    db_provider = models.Provider(**provider.model_dump())
    db.add(db_provider)
    db.commit()
    db.refresh(db_provider)
    return db_provider


def get_provider(db: Session, provider_id: int) -> Optional[models.Provider]:
    return db.query(models.Provider).filter(models.Provider.id == provider_id).first()


def get_providers(db: Session, skip: int = 0, limit: int = 100) -> List[models.Provider]:
    return db.query(models.Provider).offset(skip).limit(limit).all()


def update_provider(db: Session, provider_id: int, updates: schemas.ProviderUpdate) -> Optional[models.Provider]:
    db_provider = get_provider(db, provider_id)
    if not db_provider:
        return None
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(db_provider, field, value)
    db.commit()
    db.refresh(db_provider)
    return db_provider


def delete_provider(db: Session, provider_id: int) -> bool:
    db_provider = get_provider(db, provider_id)
    if not db_provider:
        return False
    db.delete(db_provider)
    db.commit()
    return True


# ---------- Claim ----------

def create_claim(db: Session, claim: schemas.ClaimCreate) -> models.Claim:
    db_claim = models.Claim(**claim.model_dump(), status=models.ClaimStatus.SUBMITTED)
    db.add(db_claim)
    db.commit()
    db.refresh(db_claim)
    return db_claim


def get_claim(db: Session, claim_id: int) -> Optional[models.Claim]:
    return db.query(models.Claim).filter(models.Claim.id == claim_id).first()


def get_claims(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    member_id: Optional[int] = None,
    status: Optional[models.ClaimStatus] = None,
) -> List[models.Claim]:
    query = db.query(models.Claim)
    if member_id is not None:
        query = query.filter(models.Claim.member_id == member_id)
    if status is not None:
        query = query.filter(models.Claim.status == status)
    return query.offset(skip).limit(limit).all()


def update_claim(db: Session, claim_id: int, updates: schemas.ClaimUpdate) -> Optional[models.Claim]:
    db_claim = get_claim(db, claim_id)
    if not db_claim:
        return None
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(db_claim, field, value)
    db.commit()
    db.refresh(db_claim)
    return db_claim


def delete_claim(db: Session, claim_id: int) -> bool:
    db_claim = get_claim(db, claim_id)
    if not db_claim:
        return False
    db.delete(db_claim)
    db.commit()
    return True


def adjudicate_claim(db: Session, claim_id: int) -> Optional[models.Claim]:
    """
    Very simple adjudication rule engine, meant as a starting point:

    - Member must exist and be active, otherwise DENY.
    - Provider must exist, otherwise DENY.
    - In-network providers: allowed amount = 80% of billed amount.
    - Out-of-network providers: allowed amount = 50% of billed amount.
    - Anything approved moves to APPROVED status; caller can later
      mark it PAID once payment is issued.
    """
    claim = get_claim(db, claim_id)
    if not claim:
        return None

    member = get_member(db, claim.member_id)
    provider = get_provider(db, claim.provider_id)

    if not member or not member.is_active:
        claim.status = models.ClaimStatus.DENIED
        claim.notes = "Denied: member not found or inactive."
    elif not provider:
        claim.status = models.ClaimStatus.DENIED
        claim.notes = "Denied: provider not found."
    else:
        coverage_rate = 0.8 if provider.is_in_network else 0.5
        claim.allowed_amount = round(claim.billed_amount * coverage_rate, 2)
        claim.status = models.ClaimStatus.APPROVED
        claim.notes = f"Approved at {int(coverage_rate * 100)}% coverage rate."

    db.commit()
    db.refresh(claim)
    return claim


def pay_claim(db: Session, claim_id: int) -> Optional[models.Claim]:
    """Mark an APPROVED claim as PAID, paying out the allowed amount."""
    claim = get_claim(db, claim_id)
    if not claim or claim.status != models.ClaimStatus.APPROVED:
        return None
    claim.paid_amount = claim.allowed_amount
    claim.status = models.ClaimStatus.PAID
    db.commit()
    db.refresh(claim)
    return claim
