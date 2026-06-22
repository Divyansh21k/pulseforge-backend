import os
import sys

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("GEMINI_API_KEY", "")

from app.core.database import Base, get_db
from app.main import app


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def client(db_session):
    from fastapi.testclient import TestClient

    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def organizer_headers(db_session):
    from app.models.participant import Participant
    from app.utils.security import hash_password, create_access_token

    user = Participant(
        full_name="Test Organizer",
        email="organizer@test.dev",
        hashed_password=hash_password("testpass123"),
        organization="Test",
        role="organizer",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token({"sub": str(user.id), "role": "organizer"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def reviewer_headers(db_session):
    from app.models.participant import Participant
    from app.services.reviewer_service import ReviewerService
    from app.utils.security import hash_password, create_access_token

    user = Participant(
        full_name="Test Reviewer",
        email="reviewer@test.dev",
        hashed_password=hash_password("testpass123"),
        organization="Test",
        role="reviewer",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    ReviewerService(db_session).create_reviewer(
        "Test Reviewer", "reviewer@test.dev", organization="Test",
        expertise_text="python, ml", participant_id=user.id,
    )
    token = create_access_token({"sub": str(user.id), "role": "reviewer"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def participant_headers(db_session):
    from app.models.participant import Participant
    from app.utils.security import hash_password, create_access_token

    user = Participant(
        full_name="Test Participant",
        email="participant@test.dev",
        hashed_password=hash_password("testpass123"),
        organization="Test",
        role="participant",
        raw_skills_text="python, react",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token({"sub": str(user.id), "role": "participant"})
    return {"Authorization": f"Bearer {token}"}
