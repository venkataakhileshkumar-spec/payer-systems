"""
Payer System - simple base project.

Run with:
    uvicorn app.main:app --reload

Then open http://127.0.0.1:8000/docs for interactive API docs.
"""

from fastapi import FastAPI

from app.database import Base, engine
from app.routers import members, providers, claims

# Create tables on startup (fine for a base/demo project; use Alembic
# migrations instead once this grows into a real production system).
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Payer System",
    description="A simple base project for a healthcare insurance payer: "
    "members, providers, and claims with basic adjudication.",
    version="0.1.0",
)

app.include_router(members.router)
app.include_router(providers.router)
app.include_router(claims.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "service": "Payer System API"}
