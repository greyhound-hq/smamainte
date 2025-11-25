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

# Ensure the app package can be imported
from app.main import app
from app.models import Base
from app.db import get_db

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# create tables
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# override the dependency in the FastAPI app
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c
