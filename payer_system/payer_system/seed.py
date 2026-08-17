"""
Optional: populate the SQLite DB with a bit of sample data so the API
isn't empty on first run.

Usage:
    python seed.py
"""

from datetime import date

from app.database import Base, engine, SessionLocal
from app import models

Base.metadata.create_all(bind=engine)
db = SessionLocal()

try:
    if db.query(models.Member).count() == 0:
        member = models.Member(
            member_number="M-1001",
            first_name="Asha",
            last_name="Rao",
            date_of_birth=date(1990, 5, 14),
            plan_name="Gold PPO",
            is_active=1,
        )
        provider = models.Provider(
            npi="1234567890",
            name="Sunrise Family Clinic",
            specialty="Family Medicine",
            is_in_network=1,
        )
        db.add_all([member, provider])
        db.commit()
        db.refresh(member)
        db.refresh(provider)

        claim = models.Claim(
            claim_number="CLM-0001",
            member_id=member.id,
            provider_id=provider.id,
            service_date=date(2026, 8, 1),
            diagnosis_code="J06.9",
            procedure_code="99213",
            billed_amount=250.00,
            status=models.ClaimStatus.SUBMITTED,
        )
        db.add(claim)
        db.commit()
        print("Seeded 1 member, 1 provider, 1 claim.")
    else:
        print("Data already present, skipping seed.")
finally:
    db.close()
