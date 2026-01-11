import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.db import get_db
from app.models import Base  # Must match where Base is defined in your project

@pytest.fixture(scope="session")
def db_engine():
   """
   Creates a shared in-memory SQLite database for tests.
   Why this is necessary:
   - sqlite:///:memory: normally creates a NEW empty database per connection.
     That means your tables can "disappear" between the table creation step
     and the API request step.
   - StaticPool forces SQLAlchemy to reuse ONE shared connection, so the tables
     created by Base.metadata.create_all(...) are still there during API calls.
   - check_same_thread=False avoids thread errors when FastAPI TestClient runs.
   """
   engine = create_engine(
       "sqlite+pysqlite:///:memory:",
       connect_args={"check_same_thread": False},
       poolclass=StaticPool,
   )
   # Create all tables defined on Base (including line_status_requests)
   Base.metadata.create_all(bind=engine)
   return engine

@pytest.fixture()
def db_session(db_engine):
   """
   Creates a new database session per test (isolation).
   """
   TestingSessionLocal = sessionmaker(
       autocommit=False,
       autoflush=False,
       bind=db_engine,
   )
   db = TestingSessionLocal()
   try:
       yield db
   finally:
       db.close()

@pytest.fixture()
def client(db_session):
   """
   Overrides the app's DB dependency so API endpoints use the test DB.
   """
   def override_get_db():
       yield db_session
   app.dependency_overrides[get_db] = override_get_db
   with TestClient(app) as c:
       yield c
   app.dependency_overrides.clear()