from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings

class Base(DeclarativeBase):
   """Base class for SQLAlchemy models."""
   pass

# Engine = connection manager to the database.
engine = create_engine(settings.database_url, pool_pre_ping=True)
# SessionLocal = creates per-request DB sessions.
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db():
   """
   Dependency for FastAPI endpoints.
   Ensures each request gets a DB session and it closes safely.
   Failure mode:
   - If DB is down, session creation will fail and the API should return 500.
   """
   db = SessionLocal()
   try:
       yield db
   finally:
       db.close()