import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db import get_db
from app.models import Base  # this must match where Base is defined in your project

@pytest.fixture(scope="session")
def db_engine():
   """
   Creates a SQLite database for tests.
   Why:
   - Keeps tests deterministic (no real Postgres needed in CI).
   - Creates tables once for the test session.
   - check_same_thread=False avoids SQLite thread errors with FastAPI TestClient.
   """
   engine = create_engine(
       "sqlite+pysqlite:///:memory:",
       connect_args={"check_same_thread": False},
   )
   Base.metadata.create_all(bind=engine)
   return engine

@pytest.fixture()
def db_session(db_engine):
   """
   New database session per test.
   This prevents tests affecting each other (isolation).
   """
   TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
   db = TestingSessionLocal()
   try:
       yield db
   finally:
       db.close()

@pytest.fixture()
def client(db_session):
   """
   Overrides the app's database dependency so the API uses the test DB.
   """
   def override_get_db():
       yield db_session
   app.dependency_overrides[get_db] = override_get_db
   with TestClient(app) as c:
       yield c
   app.dependency_overrides.clear()