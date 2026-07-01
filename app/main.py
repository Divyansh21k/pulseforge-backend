from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import Base, engine, SessionLocal
from app import models
from app.models import communication
from app.routers.v1 import participants, duplicates, skills, teams, events, projects, reviewers, evaluations, results, analytics, audit, gemini
from app.routers.v1 import auth as auth_router
from app.routers.v1 import communications as communications_router
from app.routers.v1 import bias_stream as bias_stream_router
from app.routers.v1 import demo as demo_router
from app.routers.v1 import voice as voice_router
from app.repositories.participant_repository import ParticipantRepository

Base.metadata.create_all(bind=engine)


def _auto_seed_if_empty():
    """Demo reliability: load sample dataset when bulk seed data is absent."""
    db = SessionLocal()
    try:
        repo = ParticipantRepository(db)
        if repo.get_by_email("participant1@hackathon.dev") is None:
            from scripts.seed_data import run as run_seed
            run_seed()
    except Exception as exc:
        print(f"[PulseForge] Auto-seed skipped: {exc}")
    finally:
        db.close()


_auto_seed_if_empty()

app = FastAPI(title="PulseForge", version="1.0.0", description="AI-powered Hackathon Management Platform")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(auth_router.router)
app.include_router(demo_router.router)
app.include_router(participants.router)
app.include_router(duplicates.router)
app.include_router(skills.router)
app.include_router(teams.router)
app.include_router(events.router)
app.include_router(projects.router)
app.include_router(reviewers.router)
app.include_router(evaluations.router)
app.include_router(results.router)
app.include_router(analytics.router)
app.include_router(communications_router.router)
app.include_router(bias_stream_router.router)
app.include_router(audit.router)
app.include_router(gemini.router)
app.include_router(voice_router.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "pulseforge-backend"}
