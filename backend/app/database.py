from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings
from app.logger import get_logger

logger = get_logger("database")

database_url = settings.DATABASE_URL
connect_args = {}

if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://","postgresql://",1)
    connect_args = {"check_same_thread": False}

try:
    engine = create_engine(
        database_url,
        connect_args=connect_args,
        pool_pre_ping=True  # Automatically checks connection health before issuing queries
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
    logger.info("Successfully established connection engine to SQLite database.")
except Exception as e:
    logger.critical(f"Critical error initializing Database connection engine: {e}", exc_info=True)
    raise e

def get_db():
    """FastAPI Dependency yielding thread-safe db sessions and ensuring prompt closure."""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session encountered an error: {e}")
        raise
    finally:
        db.close()
