"""Shared pytest fixtures for SustainTwin AI backend tests."""

import os
import sys
import pytest
from unittest.mock import MagicMock, patch

# Ensure backend is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Override DATABASE_URL before any app imports
os.environ["DATABASE_URL"] = "sqlite:///./test_sustain.db"
os.environ["REDIS_URL"] = ""
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["GEMINI_API_KEY"] = "test-key"


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Create all tables in a test SQLite database."""
    # Patch database.py to use SQLite for tests
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker, declarative_base

    test_engine = create_engine("sqlite:///./test_sustain.db", connect_args={"check_same_thread": False})

    import app.core.database as db_module
    db_module.engine = test_engine
    db_module.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    from app.core.database import Base
    import app.models.machine  # noqa: F401
    import app.models.user  # noqa: F401
    import app.models.diagnosis  # noqa: F401

    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)
    try:
        import pathlib
        pathlib.Path("./test_sustain.db").unlink(missing_ok=True)
    except PermissionError:
        pass  # Windows file locking — file will be cleaned up next run


@pytest.fixture
def db_session():
    """Provide a clean DB session for each test."""
    from app.core.database import SessionLocal
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def seed_users(db_session):
    """Seed test users with different roles."""
    from app.models.user import User
    from app.core.security import get_password_hash

    users = [
        User(username="test_operator", hashed_password=get_password_hash("pass123"), role="operator"),
        User(username="test_engineer", hashed_password=get_password_hash("pass123"), role="engineer"),
        User(username="test_admin", hashed_password=get_password_hash("pass123"), role="admin"),
    ]
    for u in users:
        existing = db_session.query(User).filter(User.username == u.username).first()
        if not existing:
            db_session.add(u)
    db_session.commit()
    return users


@pytest.fixture
def seed_machines(db_session):
    """Seed test machines."""
    from app.models.machine import Machine

    machines = [
        Machine(id="T-001", machine_type="Excavator", status="Nominal"),
        Machine(id="T-002", machine_type="Haul Truck", status="Nominal"),
    ]
    for m in machines:
        existing = db_session.query(Machine).filter(Machine.id == m.id).first()
        if not existing:
            db_session.add(m)
    db_session.commit()
    return machines


@pytest.fixture
def auth_token_operator(seed_users):
    """JWT token for operator role."""
    from app.core.security import create_access_token
    return create_access_token(data={"sub": "test_operator", "role": "operator"})


@pytest.fixture
def auth_token_engineer(seed_users):
    """JWT token for engineer role."""
    from app.core.security import create_access_token
    return create_access_token(data={"sub": "test_engineer", "role": "engineer"})


@pytest.fixture
def auth_token_admin(seed_users):
    """JWT token for admin role."""
    from app.core.security import create_access_token
    return create_access_token(data={"sub": "test_admin", "role": "admin"})


@pytest.fixture
def client(seed_users, seed_machines):
    """FastAPI test client."""
    from fastapi.testclient import TestClient
    from app.main import app
    from app.core.database import get_db, SessionLocal

    def override_get_db():
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
