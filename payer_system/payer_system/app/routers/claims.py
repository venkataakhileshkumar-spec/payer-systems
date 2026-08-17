from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas, models
from app.database import get_db

router = APIRouter(prefix="/claims", tags=["Claims"])


@router.post("/", response_model=schemas.ClaimOut, status_code=201)
def create_claim(claim: schemas.ClaimCreate, db: Session = Depends(get_db)):
    # Basic referential checks up front for a friendlier error than a DB constraint failure.
    if not crud.get_member(db, claim.member_id):
        raise HTTPException(status_code=400, detail="member_id does not exist")
    if not crud.get_provider(db, claim.provider_id):
        raise HTTPException(status_code=400, detail="provider_id does not exist")
    return crud.create_claim(db, claim)


@router.get("/", response_model=list[schemas.ClaimOut])
def list_claims(
    skip: int = 0,
    limit: int = 100,
    member_id: Optional[int] = None,
    status: Optional[models.ClaimStatus] = None,
    db: Session = Depends(get_db),
):
    return crud.get_claims(db, skip, limit, member_id, status)


@router.get("/{claim_id}", response_model=schemas.ClaimOut)
def get_claim(claim_id: int, db: Session = Depends(get_db)):
    claim = crud.get_claim(db, claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return claim


@router.patch("/{claim_id}", response_model=schemas.ClaimOut)
def update_claim(claim_id: int, updates: schemas.ClaimUpdate, db: Session = Depends(get_db)):
    claim = crud.update_claim(db, claim_id, updates)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return claim


@router.post("/{claim_id}/adjudicate", response_model=schemas.ClaimOut)
def adjudicate_claim(claim_id: int, db: Session = Depends(get_db)):
    """Run the claim through the (simple) adjudication rules engine."""
    claim = crud.adjudicate_claim(db, claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return claim


@router.post("/{claim_id}/pay", response_model=schemas.ClaimOut)
def pay_claim(claim_id: int, db: Session = Depends(get_db)):
    """Pay out an APPROVED claim. Fails if the claim isn't approved yet."""
    claim = crud.pay_claim(db, claim_id)
    if not claim:
        raise HTTPException(
            status_code=400,
            detail="Claim must exist and be in APPROVED status to be paid",
        )
    return claim


@router.delete("/{claim_id}", status_code=204)
def delete_claim(claim_id: int, db: Session = Depends(get_db)):
    if not crud.delete_claim(db, claim_id):
        raise HTTPException(status_code=404, detail="Claim not found")
