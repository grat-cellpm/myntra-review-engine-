import os
import json
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.session import Base
from database.product_models import ProductReview, ProductInsight, ProductSummary
from processing.deduplicator import ReviewFilter
from ai.review_analyzer import ReviewAnalyzer

load_dotenv()

DB_FILE = "myntra_discovery_basic.db"
# Use same DB but create tables if they don't exist
engine = create_engine(f"sqlite:///{DB_FILE}")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def fetch_mock_product_reviews(product_id: str, limit: int = 500) -> list[dict]:
    """
    Mock function to simulate fetching product reviews. 
    In reality, this would call an API or a scraper.
    """
    print(f"Fetching up to {limit} reviews for product {product_id}...")
    # Generating some mock reviews including duplicates and short generic ones
    mock_reviews = [
        {"author_identifier": "user1", "original_review": "The fit is way too small. I ordered a medium and it fits like a small. Fabric is okay though.", "rating": 3, "review_date": "2024-01-01T10:00:00Z"},
        {"author_identifier": "user2", "original_review": "Very good product", "rating": 5, "review_date": "2024-01-02T11:00:00Z"}, # Should be filtered out
        {"author_identifier": "user3", "original_review": "Absolutely love the color, it matches the picture perfectly. But after one wash, the stitching came undone.", "rating": 2, "review_date": "2024-01-03T12:00:00Z"},
        {"author_identifier": "user1_dup", "original_review": "The fit is way too small. I ordered a medium and it fits like a small. Fabric is okay though.", "rating": 3, "review_date": "2024-01-04T10:00:00Z"}, # Exact duplicate
        {"author_identifier": "user4", "original_review": "nice", "rating": 4, "review_date": "2024-01-05T10:00:00Z"}, # Should be filtered out
        {"author_identifier": "user5", "original_review": "Great value for the price. I wore it to a party and got many compliments. Highly recommend if you are looking for a cheap but stylish option.", "rating": 5, "review_date": "2024-01-06T10:00:00Z"},
        {"author_identifier": "user6", "original_review": "The material is very thin, almost see-through. I am returning this. Not worth 1500 rupees.", "rating": 1, "review_date": "2024-01-07T10:00:00Z"},
        {"author_identifier": "user6_near_dup", "original_review": "The material is very thin, it's almost see-through. I am returning it. Not worth 1500 rs.", "rating": 1, "review_date": "2024-01-08T10:00:00Z"}, # Near duplicate
    ]
    
    # Duplicate the mock array to simulate a larger fetch, modifying dates slightly
    expanded_reviews = []
    for i in range(20):
        for idx, r in enumerate(mock_reviews):
            expanded_reviews.append({
                "author_identifier": f"{r['author_identifier']}_{i}",
                "original_review": r['original_review'],
                "rating": r['rating'],
                "review_date": f"2024-01-{str(i+1).zfill(2)}T10:00:00Z"
            })
            
    return expanded_reviews[:limit]

def run_product_pipeline(product_id: str):
    db = SessionLocal()
    try:
        # 1. Fetch
        raw_reviews = fetch_mock_product_reviews(product_id, limit=500)
        print(f"Fetched {len(raw_reviews)} raw reviews.")
        
        # 2. Deduplicate & Filter
        filter_engine = ReviewFilter(similarity_threshold=0.85, min_words=4)
        filtered_reviews = filter_engine.process_reviews(raw_reviews)
        print(f"After deduplication & filtering, {len(filtered_reviews)} reviews remain.")
        
        analyzer = ReviewAnalyzer()
        
        saved_reviews = []
        insights_data = []
        
        for rev_dict in filtered_reviews:
            text = rev_dict.get('original_review', '')
            
            # 3. Score Quality & Authenticity
            print(f"Scoring review: {text[:30]}...")
            score = analyzer.score_review(text)
            
            # If scoring failed, we might skip or give default. We will skip for safety.
            if not score:
                continue
                
            db_review = ProductReview(
                product_id=product_id,
                source='mock',
                original_review=text,
                rating=rev_dict.get('rating'),
                author_identifier=rev_dict.get('author_identifier'),
                quality_score=score.quality_score,
                authenticity_confidence=score.authenticity_confidence
            )
            db.add(db_review)
            db.flush() # To get the ID
            saved_reviews.append(rev_dict)
            
            # 4. Extract Insights (only for high quality reviews or all remaining)
            # Let's extract for all remaining
            print("Extracting insights...")
            insight = analyzer.extract_insights(text)
            if insight:
                db_insight = ProductInsight(
                    review_id=db_review.id,
                    fit_size=insight.fit_size,
                    fabric_comfort=insight.fabric_comfort,
                    quality_durability=insight.quality_durability,
                    color_accuracy=insight.color_accuracy,
                    price_value=insight.price_value,
                    actual_usage=insight.actual_usage
                )
                db.add(db_insight)
                insights_data.append(insight.model_dump())
        
        db.commit()
        
        # 5. Cluster & Summarize
        print("Generating evidence-based summary...")
        markdown_summary, themes = analyzer.generate_summary(product_id, saved_reviews, insights_data)
        
        if markdown_summary:
            db_summary = ProductSummary(
                product_id=product_id,
                summary_markdown=markdown_summary,
                themes=themes
            )
            db.add(db_summary)
            db.commit()
            print("Summary generated and saved successfully.")
            print("\n" + "="*50)
            print("EVIDENCE-BASED SUMMARY")
            print("="*50)
            print(markdown_summary)
            print("="*50)
            
    except Exception as e:
        print(f"Pipeline failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    if not os.getenv("GROQ_API_KEY"):
        print("ERROR: GROQ_API_KEY is not set.")
    else:
        # Example Product ID
        run_product_pipeline("MYNTRA-PROD-12345")
