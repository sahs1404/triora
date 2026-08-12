from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite is enough for a hackathon prototype — no need for Postgres here.
# The .db file will be created automatically on first run, in backend/.
DATABASE_URL = "sqlite:///./triora.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency — yields a DB session per request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()