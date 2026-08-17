from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/members", tags=["Members"])


@router.post("/", response_model=schemas.MemberOut, status_code=201)
def create_member(member: schemas.MemberCreate, db: Session = Depends(get_db)):
    return crud.create_member(db, member)


@router.get("/", response_model=list[schemas.MemberOut])
def list_members(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_members(db, skip, limit)


@router.get("/{member_id}", response_model=schemas.MemberOut)
def get_member(member_id: int, db: Session = Depends(get_db)):
    member = crud.get_member(db, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return member


@router.patch("/{member_id}", response_model=schemas.MemberOut)
def update_member(member_id: int, updates: schemas.MemberUpdate, db: Session = Depends(get_db)):
    member = crud.update_member(db, member_id, updates)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return member


@router.delete("/{member_id}", status_code=204)
def delete_member(member_id: int, db: Session = Depends(get_db)):
    if not crud.delete_member(db, member_id):
        raise HTTPException(status_code=404, detail="Member not found")
