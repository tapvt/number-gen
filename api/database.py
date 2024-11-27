from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
import urllib.parse

# Use the Neon Postgres connection URL
DATABASE_URL = os.environ.get(
    'POSTGRES_URL',
    'postgresql://neondb_owner:password@ep-patient-fire-a6iqw79a.us-east-2.aws.neon.tech/neondb?sslmode=require'
)

# Parse the connection URL to ensure compatibility
parsed_url = urllib.parse.urlparse(DATABASE_URL)
clean_url = f"postgresql://{parsed_url.username}:{urllib.parse.quote(parsed_url.password or '')}@{parsed_url.hostname}/{parsed_url.path.lstrip('/')}"

engine = create_engine(clean_url, pool_pre_ping=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    # Import models here to avoid circular imports
    from api.models import Customer, Order, User
    Base.metadata.create_all(bind=engine)
