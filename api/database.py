from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
import urllib.parse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use the Neon Postgres connection URL
def get_database_url():
    """
    Retrieve and validate the database connection URL.

    Raises:
        ValueError: If the database URL is not properly configured
    """
    DATABASE_URL = os.environ.get('POSTGRES_URL')

    if not DATABASE_URL:
        logger.error("POSTGRES_URL environment variable is not set!")
        raise ValueError("Database connection URL is required. Set POSTGRES_URL environment variable.")

    # Optional: Add additional validation for the URL
    try:
        parsed_url = urllib.parse.urlparse(DATABASE_URL)
        if not all([parsed_url.scheme, parsed_url.hostname]):
            raise ValueError("Invalid database URL format")
    except Exception as e:
        logger.error(f"Invalid database URL: {e}")
        raise

    return DATABASE_URL

try:
    # Get and validate the database URL
    database_url = get_database_url()

    # Create SQLAlchemy engine with connection pooling and error handling
    engine = create_engine(
        database_url,
        pool_pre_ping=True,  # Test connections before using them
        pool_recycle=3600,   # Recycle connections after 1 hour
        pool_size=5,          # Maintain a pool of 5 connections
        max_overflow=10       # Allow up to 10 additional connections
    )

    # Create session factory
    db_session = scoped_session(sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    ))

    Base = declarative_base()
    Base.query = db_session.query_property()

    def init_db():
        """
        Initialize the database by creating all tables.
        Import models here to avoid circular imports.
        """
        try:
            from api.models import Customer, Order, User
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            raise

except Exception as e:
    logger.error(f"Fatal database configuration error: {e}")
    raise
