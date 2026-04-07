"""
Core Database Setup (Reusable for Smart Waste Segregation or any system)
Production-ready SQLAlchemy setup with pooling, retry logic, and session control.
"""

import os
import time
import logging
from contextlib import contextmanager

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from sqlalchemy.exc import OperationalError

# ----------------------------
# Logging Setup
# ----------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DB")

# ----------------------------
# Environment Config
# ----------------------------
DB_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./waste.db"  # You can rename later if needed
)

POOL_SIZE = int(os.getenv("DB_POOL_SIZE", 10))
MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", 20))
POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", 30))
POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", 1800))

# ----------------------------
# Engine Setup
# ----------------------------
engine = create_engine(
    DB_URL,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_timeout=POOL_TIMEOUT,
    pool_recycle=POOL_RECYCLE,
    pool_pre_ping=True,
    echo=False,
    future=True
)

# ----------------------------
# Session Factory
# ----------------------------
SessionLocal = scoped_session(sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
))

# ----------------------------
# Base Model
# ----------------------------
Base = declarative_base()

# ----------------------------
# Retry Decorator
# ----------------------------
def retry_db(max_retries=3, delay=2):
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except OperationalError as e:
                    retries += 1
                    logger.warning(f"DB retry {retries}/{max_retries}: {e}")
                    time.sleep(delay)
            raise Exception("Database operation failed after retries")
        return wrapper
    return decorator

# ----------------------------
# Session Context Manager
# ----------------------------
@contextmanager
def get_db_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"DB transaction failed: {e}")
        raise
    finally:
        session.close()

# ----------------------------
# Event Hooks
# ----------------------------
@event.listens_for(engine, "connect")
def connect_event(dbapi_connection, connection_record):
    logger.info("Database connection established")

@event.listens_for(engine, "checkout")
def checkout_event(dbapi_connection, connection_record, connection_proxy):
    logger.debug("Connection checked out from pool")

# ----------------------------
# Health Check
# ----------------------------
def check_db_health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"DB health check failed: {e}")
        return False

# ----------------------------
# Init DB
# ----------------------------
def init_db():
    import backend.models  # ensures models are registered

    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully")

# ----------------------------
# Drop DB
# ----------------------------
def drop_db():
    logger.warning("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    logger.warning("Database dropped")

# ----------------------------
# Raw Query Executor (SAFE FIX)
# ----------------------------
@retry_db()
def execute_raw_query(query: str):
    with engine.connect() as conn:
        result = conn.execute(text(query))  # FIX: required in SQLAlchemy 2.0
        try:
            return result.fetchall()
        except Exception:
            return None