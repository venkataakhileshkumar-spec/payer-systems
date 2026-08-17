# Payer System

A simple base project for a healthcare insurance **payer** — the entity
(insurance company) that pays claims submitted by providers on behalf
of insured members.

## What's included

- **Members** — the insured individuals and their plan info
- **Providers** — doctors/clinics who deliver care and submit claims
- **Claims** — requests for payment, with a basic adjudication engine:
  - Denies claims for inactive/unknown members or unknown providers
  - Approves claims for in-network providers at 80% of billed amount
  - Approves claims for out-of-network providers at 50% of billed amount
  - Supports moving an approved claim to `PAID`

Built with **FastAPI + SQLAlchemy + SQLite** so it runs with zero external
services and gives you interactive API docs out of the box.

## Project structure

```
payer_system/
├── app/
│   ├── main.py          # FastAPI app + router registration
│   ├── database.py       # SQLAlchemy engine/session setup
│   ├── models.py         # ORM models: Member, Provider, Claim
│   ├── schemas.py        # Pydantic request/response schemas
│   ├── crud.py            # Data access + adjudication logic
│   └── routers/
│       ├── members.py
│       ├── providers.py
│       └── claims.py
├── seed.py                # Optional sample data loader
├── requirements.txt
└── README.md
```

## Getting started

```bash
# 1. Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) seed some sample data
python seed.py

# 4. Run the API
uvicorn app.main:app --reload
```

Then open **http://127.0.0.1:8000/docs** for interactive Swagger docs
where you can try every endpoint.

## Example workflow

```bash
# Create a member
curl -X POST http://127.0.0.1:8000/members/ \
  -H "Content-Type: application/json" \
  -d '{"member_number":"M-2001","first_name":"Ravi","last_name":"Kumar","date_of_birth":"1985-03-20","plan_name":"Silver HMO"}'

# Create a provider
curl -X POST http://127.0.0.1:8000/providers/ \
  -H "Content-Type: application/json" \
  -d '{"npi":"9988776655","name":"City Hospital","specialty":"Cardiology","is_in_network":true}'

# Submit a claim
curl -X POST http://127.0.0.1:8000/claims/ \
  -H "Content-Type: application/json" \
  -d '{"claim_number":"CLM-1000","member_id":1,"provider_id":1,"service_date":"2026-08-10","billed_amount":500}'

# Adjudicate it
curl -X POST http://127.0.0.1:8000/claims/1/adjudicate

# Pay it
curl -X POST http://127.0.0.1:8000/claims/1/pay
```

## Extending this base

This is intentionally a starting point. Natural next steps:
- Add authentication (e.g. OAuth2/JWT) and role-based access (payer staff vs. provider portal)
- Move from `create_all` to Alembic migrations
- Add eligibility checks, benefit accumulators (deductible/out-of-pocket tracking)
- Add more realistic adjudication rules (fee schedules, prior authorization, COB)
- Swap SQLite for Postgres for production use
