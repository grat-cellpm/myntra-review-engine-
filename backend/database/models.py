import datetime
from sqlalchemy import Column, String, Float, DateTime, Boolean, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from .session import Base

class RawReview(Base):
    __tablename__ = "raw_reviews"

    review_id = Column(String, primary_key=True, index=True)
    source = Column(String, index=True) # google_play, app_store, reddit
    source_url = Column(String, nullable=True)
    original_review = Column(Text, nullable=False)
    rating = Column(Float, nullable=True)
    review_date = Column(DateTime, nullable=True)
    collected_at = Column(DateTime, default=datetime.datetime.utcnow)
    language = Column(String, nullable=True)
    country = Column(String, nullable=True)
    app_version = Column(String, nullable=True)
    author_identifier = Column(String, nullable=True)

class StructuredInsight(Base):
    __tablename__ = "structured_insights"
    
    # We use a synthetic primary key since one review might theoretically yield multiple insights,
    # or just use review_id as primary if it's 1-to-1. Sticking to 1-to-1 based on requirements for now,
    # but an auto-incrementing ID is safer.
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    review_id = Column(String, ForeignKey("raw_reviews.review_id"), unique=True, index=True)
    
    relevance = Column(String, index=True)
    sentiment = Column(String)
    user_intent = Column(String, index=True)
    wishlist_intent = Column(String, index=True)
    
    # For SQLite compatibility in MVP, we can store lists as comma-separated strings or JSON.
    # We will use JSON/String based on the DB type, but let's use String for simple lists for MVP
    # or rely on JSON. Since requirements say PostgreSQL, we can use JSON/JSONB.
    # To keep it generic for the fallback SQLite, we'll store as JSON encoded strings 
    # or use SQLAlchemy's JSON type (which works with SQLite in newer versions).
    from sqlalchemy import JSON
    purchase_barriers = Column(JSON)
    uncertainties = Column(JSON)
    
    comparison_behavior = Column(String)
    alternative_found = Column(Boolean)
    root_cause = Column(Text)
    opportunity_area = Column(String, index=True)
    confidence = Column(String)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
