from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "grocery.db"

engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Base declarative class for SQLAlchemy models."""


@contextmanager
def get_session() -> Iterator[Session]:
    """Provide a transactional scope around a series of operations."""

    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()