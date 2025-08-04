# tests/conftest.py

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.db.session import SessionLocal, init_db

@pytest.fixture(scope="module")
def client():
    init_db()
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(scope="module")
def db_session():
    db = SessionLocal()
    yield db
    db.close()
