import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()


def get_database_url() -> str:
    """Return the database URL from environment variables.

    Prefers ``DATABASE_URL`` but falls back to the legacy ``databse_url``
    variable (note the typo) for backward compatibility.

    Raises:
        RuntimeError: If neither variable is set.
    """
    url = os.environ.get("DATABASE_URL") or os.environ.get("databse_url")
    if url is None:
        raise RuntimeError("DATABASE_URL environment variable is required")
    return url


DATABASE_URL = get_database_url()


engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
