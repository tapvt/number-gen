from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

# Use the Neon Postgres connection URL
DATABASE_URL = os.environ.get(
    'POSTGRES_URL',
    'postgres://neondb_owner:password@ep-patient-fire-a6iqw79a/neondb?sslmode=require'
)

engine = create_engine(DATABASE_URL)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    Base.metadata.create_all(bind=engine)
