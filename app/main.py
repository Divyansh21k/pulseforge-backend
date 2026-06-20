from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app import models
from app.models import communication
from app.routers.v1 import participants, duplicates, skills, teams, projects, reviewers, evaluations, results, analytics
from app.routers.v1 import auth as auth_router
from app.routers.v1 import communications as communications_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="PulseForge", version="1.0.0", description="AI-powered Hackathon Management Platform")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(auth_router.router)
app.include_router(participants.router)
app.include_router(duplicates.router)
app.include_router(skills.router)
app.include_router(teams.router)
app.include_router(projects.router)
app.include_router(reviewers.router)
app.include_router(evaluations.router)
app.include_router(results.router)
app.include_router(analytics.router)
app.include_router(communications_router.router)

@app.get("/health")
def


rm -f pulseforge.db
python -m pytest tests/ -v
git add .
git commit -m "feat: JWT auth, communications, Dockerfile"
git push
