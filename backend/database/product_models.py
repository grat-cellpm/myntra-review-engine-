import datetime
from sqlalchemy import Column, String, Float, DateTime, Integer, Text, ForeignKey, JSON
from .session import Base

class ProductReview(Base):
    __tablename__ = "product_reviews"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(String, index=True, nullable=False)
    source = Column(String, index=True) # e.g., 'mock', 'scraper'
    original_review = Column(Text, nullable=False)
    rating = Column(Float, nullable=True)
    review_date = Column(DateTime, nullable=True)
    author_identifier = Column(String, nullable=True)
    
    # New fields for scoring
    quality_score = Column(Float, nullable=True)
    authenticity_confidence = Column(Float, nullable=True)
    
    collected_at = Column(DateTime, default=datetime.datetime.utcnow)

class ProductInsight(Base):
    __tablename__ = "product_insights"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    review_id = Column(Integer, ForeignKey("product_reviews.id"), unique=True, index=True)
    
    fit_size = Column(String, nullable=True)
    fabric_comfort = Column(String, nullable=True)
    quality_durability = Column(String, nullable=True)
    color_accuracy = Column(String, nullable=True)
    price_value = Column(String, nullable=True)
    actual_usage = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class ProductSummary(Base):
    __tablename__ = "product_summaries"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(String, index=True, nullable=False)
    summary_markdown = Column(Text, nullable=False)
    themes = Column(JSON, nullable=True) # e.g., [{"theme": "Fit", "percentage": 80}]
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
