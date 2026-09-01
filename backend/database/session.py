import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# We will use a fallback SQLite DB if POSTGRES_URL is not provided, 
# for easier initial setup, though PostgreSQL is the target.
DATABASE_URL = os.getenv("POSTGRES_URL", "sqlite:///./myntra_discovery.db")

engine = create_engine(
    DATABASE_URL, 
    # check_same_thread is needed for SQLite, ignored by Postgres
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
