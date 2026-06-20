from fastapi import FastAPI

from app.core.config import settings
from app.core.database import Base, engine
from app import models  # noqa: F401
from app.routers.v1 import participants, duplicates, skills, teams

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="AI-powered Hackathon Intelligence Platform",
)

app.include_router(participants.router)
app.include_router(duplicates.router)
app.include_router(skills.router)
app.include_router(teams.router)


@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok", "service": settings.app_name}
