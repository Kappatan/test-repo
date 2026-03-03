from __future__ import annotations

import logging
import time
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, sessionmaker

from config import get_settings
from repositories.models import Base

logger = logging.getLogger(__name__)

settings = get_settings()
engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def create_database(max_attempts: int = 10, delay_seconds: int = 2) -> None:
    for attempt in range(1, max_attempts + 1):
        try:
            Base.metadata.create_all(bind=engine)
            return
        except OperationalError:
            if attempt == max_attempts:
                raise
            logger.warning(
                "Database is not ready, retrying (%s/%s)...",
                attempt,
                max_attempts,
            )
            time.sleep(delay_seconds)
