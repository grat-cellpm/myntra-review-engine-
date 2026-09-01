import os
import sys
from dotenv import load_dotenv
from database.session import engine, Base, SessionLocal
from database.models import RawReview, StructuredInsight
from collectors.google_play import GooglePlayCollector
from ai.groq_engine import GroqEngine

# Load environment variables
load_dotenv()

def init_db():
    print("Initializing database...")
    Base.metadata.create_all(bind=engine)
    print("Database initialized.")

def run_pipeline(limit=5):
    print(f"Starting pipeline. Fetching up to {limit} reviews from Google Play...")
    
    collector = GooglePlayCollector()
    reviews_data = collector.fetch_reviews(limit=limit)
    
    print(f"Fetched {len(reviews_data)} reviews. Analyzing with Groq...")
    
    ai_engine = GroqEngine()
    db = SessionLocal()
    
    try:
        for item in reviews_data:
            # Filter out generic short reviews
            if not item['original_review'] or len(item['original_review'].split()) < 4 or len(item['original_review']) < 20:
                print(f"Review {item['review_id']} is too short/generic, skipping.")
                continue

            # 1. Save Raw Review
            raw_review = RawReview(
                review_id=item['review_id'],
                source=collector.source_name,
                source_url=item['source_url'],
                original_review=item['original_review'],
                rating=item['rating'],
                review_date=item['review_date'],
                language=item['language'],
                country=item['country'],
                app_version=item['app_version'],
                author_identifier=item['author_identifier']
            )
            
            # Check if it exists
            existing = db.query(RawReview).filter(RawReview.review_id == raw_review.review_id).first()
            if not existing:
                db.add(raw_review)
                db.commit()
                db.refresh(raw_review)
                print(f"Saved raw review: {raw_review.review_id}")
            else:
                print(f"Review {raw_review.review_id} already exists. Skipping.")
                continue
                
            # 2. Analyze Review
            print(f"Analyzing review {raw_review.review_id}...")
            # We enforce JSON mode in prompt by instructing groq engine
            # Groq model might need help to output pure json for pydantic
            analysis = ai_engine.analyze_review(item['original_review'])
            
            if analysis:
                # 3. Save Structured Insight
                insight = StructuredInsight(
                    review_id=raw_review.review_id,
                    relevance=analysis.relevance,
                    sentiment=analysis.sentiment,
                    user_intent=analysis.user_intent,
                    wishlist_intent=analysis.wishlist_intent,
                    purchase_barriers=analysis.purchase_barriers,
                    uncertainties=analysis.uncertainties,
                    comparison_behavior=analysis.comparison_behavior,
                    alternative_found=analysis.alternative_found,
                    root_cause=analysis.root_cause,
                    opportunity_area=analysis.opportunity_area,
                    confidence=analysis.confidence
                )
                db.add(insight)
                db.commit()
                print(f"Saved insight for review: {raw_review.review_id}")
            else:
                print(f"Failed to analyze review: {raw_review.review_id}")
                
    finally:
        db.close()
    
    print("Pipeline completed.")

if __name__ == "__main__":
    if not os.getenv("GROQ_API_KEY"):
        print("ERROR: GROQ_API_KEY environment variable not set. Please set it in your .env file.")
        sys.exit(1)
        
    init_db()
    run_pipeline(limit=3) # small batch for testing
