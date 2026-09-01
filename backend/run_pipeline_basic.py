import os
import sqlite3
import json
import requests
from dotenv import load_dotenv
from google_play_scraper import reviews, Sort

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

DB_FILE = os.path.join(os.path.dirname(__file__), "myntra_discovery_basic.db")

def init_db():
    print("Initializing SQLite database...")
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('DROP TABLE IF EXISTS raw_reviews')
    cursor.execute('DROP TABLE IF EXISTS structured_insights')
    
    cursor.execute('''
        CREATE TABLE raw_reviews (
            review_id TEXT PRIMARY KEY,
            source TEXT,
            original_review TEXT,
            rating REAL,
            review_date TEXT,
            author_identifier TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE structured_insights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            review_id TEXT,
            relevance TEXT,
            sentiment TEXT,
            user_intent TEXT,
            wishlist_intent TEXT,
            purchase_barriers TEXT,
            uncertainties TEXT,
            comparison_behavior TEXT,
            root_cause TEXT,
            opportunity_name TEXT,
            opportunity_description TEXT,
            customer_impact_score INTEGER,
            wishlist_to_purchase_impact TEXT,
            confidence TEXT,
            FOREIGN KEY(review_id) REFERENCES raw_reviews(review_id)
        )
    ''')
    conn.commit()
    conn.close()
    print("Database initialized.")

from google_play_scraper import reviews as gp_reviews, Sort
from app_store_scraper import AppStore

def fetch_reviews(limit=1000):
    print(f"Fetching {limit//2} reviews from Google Play Store...")
    play_result, _ = gp_reviews(
        "com.myntra.android",
        lang='en',
        country='in',
        sort=Sort.NEWEST,
        count=limit//2
    )
    
    print(f"Fetching {limit//2} reviews from Apple App Store...")
    app_store = AppStore(country='in', app_name='myntra', app_id='907394059')
    app_store.review(how_many=limit//2)
    apple_result = app_store.reviews
    
    combined = []
    
    # Normalize Google Play reviews
    for r in play_result:
        combined.append({
            'reviewId': r.get('reviewId'),
            'content': r.get('content', ''),
            'score': r.get('score', 0),
            'at': r.get('at', ''),
            'userName': r.get('userName', 'Anonymous'),
            'source': 'google_play'
        })
        
    # Normalize Apple App Store reviews
    import uuid
    for r in apple_result:
        combined.append({
            'reviewId': str(uuid.uuid4()), # Apple doesn't always provide a stable ID in this scraper
            'content': r.get('review', ''),
            'score': r.get('rating', 0),
            'at': r.get('date', ''),
            'userName': r.get('userName', 'Anonymous'),
            'source': 'app_store'
        })
        
    return combined

def analyze_with_groq(review_text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    schema = {
        "relevance": "Relevant to fashion shopping, Not relevant, Unclear",
        "sentiment": "positive, neutral, negative, mixed",
        "user_intent": "discovery, consideration, wishlist, purchase, comparison, complaint",
        "wishlist_intent": "genuine_purchase_intent, save_for_later, bookmarking, price_watch, comparison_shortlist, inspiration",
        "purchase_barriers": ["price, fit_size, quality, trust, lack_of_information, decision_overload, availability"],
        "uncertainties": ["List of unresolved questions"],
        "comparison_behavior": "comparing_products, comparing_brands, comparing_prices, comparing_features, comparing_styles, no_comparison",
        "root_cause": "Underlying reason behind behavior",
        "opportunity_name": "A short, dynamic 2-4 word name for the opportunity area (e.g. 'Size Chart Clarity', 'Delivery Speed', 'Product Image Accuracy')",
        "opportunity_description": "A clear description of what this opportunity entails and the core customer problem it solves",
        "customer_impact_score": "Integer from 1-10 assessing how much this problem impacts the user experience",
        "wishlist_to_purchase_impact": "High, Medium, Low - assessing how likely fixing this would convert a wishlist item to purchase",
        "confidence": "high, medium, low"
    }

    prompt = f"""
    Analyze this e-commerce review: "{review_text}"
    Extract insights exactly matching this JSON structure: {json.dumps(schema)}
    
    To arrive at your conclusion, follow this logical flow:
    1. Which theme?
    2. What behavior?
    3. What is the barrier?
    4. What uncertainty exists?
    5. What is the root cause?
    6. What opportunity does it indicate?
    """
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "openai/gpt-oss-20b",
        "messages": [
            {"role": "system", "content": "You are a JSON-only API. Only output valid JSON matching the schema. Follow a strict logical sequence to deduce the fields."},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0
    }
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return json.loads(response.json()['choices'][0]['message']['content'])
    else:
        print(f"Groq API Error: {response.text}")
        return None

def run_pipeline():
    init_db()
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    reviews_data = fetch_reviews(1000)
    
    seen_texts = set()
    generic_words = {"good", "bad", "nice", "amazing", "awesome", "terrible", "ok", "okay", "love it", "hate it", "worst", "best", "super", "excellent", "poor"}
    
    for item in reviews_data:
        review_id = item.get('reviewId')
        content = item.get('content', '')
        rating = item.get('score')
        date_str = str(item.get('at'))
        author = item.get('userName')
        source = item.get('source', 'unknown')
        
        if not content:
            continue
            
        # 1. Exclude one-line/generic reviews
        text_lower = content.lower().strip()
        word_count = len(text_lower.split())
        
        if word_count < 4 or text_lower in generic_words:
            print(f"Review {review_id} is too short/generic, skipping.")
            continue
            
        # 2. Remove exact and near-duplicate reviews
        normalized_text = "".join(c for c in text_lower if c.isalnum() or c.isspace()).strip()
        if normalized_text in seen_texts:
            print(f"Review {review_id} is a duplicate, skipping.")
            continue
            
        seen_texts.add(normalized_text)
        
        # Save raw review
        try:
            cursor.execute('''
                INSERT INTO raw_reviews (review_id, source, original_review, rating, review_date, author_identifier)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (review_id, source, content, rating, date_str, author))
            conn.commit()
            print(f"Saved raw review {review_id}")
        except sqlite3.IntegrityError:
            print(f"Review {review_id} already exists, skipping.")
            continue
            
        # Analyze with Groq
        print(f"Analyzing review {review_id} with Groq...")
        analysis = analyze_with_groq(content)
        
        if analysis:
            # Save insight
            cursor.execute('''
                INSERT INTO structured_insights (
                    review_id, relevance, sentiment, user_intent, wishlist_intent, 
                    purchase_barriers, uncertainties, comparison_behavior, 
                    root_cause, opportunity_name, opportunity_description, customer_impact_score, wishlist_to_purchase_impact, confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                review_id,
                analysis.get('relevance', ''),
                analysis.get('sentiment', ''),
                analysis.get('user_intent', ''),
                analysis.get('wishlist_intent', ''),
                json.dumps(analysis.get('purchase_barriers', [])),
                json.dumps(analysis.get('uncertainties', [])),
                analysis.get('comparison_behavior', ''),
                analysis.get('root_cause', ''),
                analysis.get('opportunity_name', ''),
                analysis.get('opportunity_description', ''),
                analysis.get('customer_impact_score', 0),
                analysis.get('wishlist_to_purchase_impact', ''),
                analysis.get('confidence', '')
            ))
            conn.commit()
            print(f"Saved insight for {review_id}\n{json.dumps(analysis, indent=2)}\n")
            import time
            time.sleep(11) # Strict rate limiting for Groq TPM limits
            
    conn.close()
    print("Pipeline finished successfully!")

if __name__ == "__main__":
    if not GROQ_API_KEY:
        print("Please set GROQ_API_KEY in backend/.env")
    else:
        run_pipeline()
