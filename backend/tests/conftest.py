import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import os
import sys

# Ensure the backend directory is on sys.path so `import app` works in CI
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Provide minimal env defaults for tests so pydantic Settings validation passes in CI
os.environ.setdefault('GCS_BUCKET', 'test-bucket')
os.environ.setdefault('DATABASE_URL', 'sqlite:///:memory:')

# Import models first so we can create test DB/tables before app imports DB engine
from app.models import Base

# Use a file-backed SQLite for tests to avoid separate in-memory connections issues
TEST_DATABASE_URL = os.environ.get('TEST_DATABASE_URL', 'sqlite:///./test_db.sqlite')

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# create tables on the test engine before importing the app to ensure tables exist
Base.metadata.create_all(bind=engine)

# Now import the FastAPI app and the real get_db so we can override it
from app.main import app
from app.db import get_db
from app.auth import require_admin


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_require_admin():
    """Mock admin dependency for tests - always returns a valid admin user."""
    return {"uid": "test-admin-uid", "email": "test@example.com"}


# override the dependencies in the FastAPI app
app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[require_admin] = override_require_admin


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c
