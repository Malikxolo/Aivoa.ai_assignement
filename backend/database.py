from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings

# Using SQLite for local testing without requiring a postgres server
engine = create_engine("sqlite:///./hcp_crm.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables. Called on app startup."""
    from models import Base as ModelBase  # noqa: F811

    ModelBase.metadata.create_all(bind=engine)
