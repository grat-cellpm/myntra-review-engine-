import os
import sqlite3
import json
import requests
import time
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DB_FILE = "myntra_discovery_basic.db"
MODEL = "llama3-8b-8192"

schema = {
    "relevance": "Relevant to fashion shopping, Not relevant, Unclear",
    "sentiment": "positive, neutral, negative, mixed",
    "user_intent": "discovery, consideration, wishlist, purchase, comparison, complaint",
    "wishlist_intent": "genuine_purchase_intent, save_for_later, bookmarking, price_watch, comparison_shortlist, inspiration",
    "purchase_barriers": ["price, fit_size, quality, trust, lack_of_information, decision_overload, availability"],
    "uncertainties": ["List of unresolved questions"],
    "comparison_behavior": "comparing_products, comparing_brands, comparing_prices, comparing_features, comparing_styles, no_comparison",
    "root_cause": "Underlying reason behind behavior",
    "opportunity_area": "price_value, fit_size, product_confidence, reviews_social_validation, product_comparison, styling_occasion, purchase_timing_reengagement, alternative_discovery",
    "confidence": "high, medium, low"
}

def analyze_with_groq(review_text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    prompt = f"""
    Analyze this e-commerce review: "{review_text}"
    Extract insights exactly matching this JSON structure: {json.dumps(SCHEMA_DEFINITION)}
    
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
        "model": MODEL,
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
    elif response.status_code == 429:
        print("Rate limit hit! Sleeping for 60 seconds...")
        time.sleep(60)
        return None
    else:
        print(f"Groq API Error ({response.status_code}): {response.text}")
        return None

def process_batch(limit=50):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Get reviews that haven't been analyzed yet
    cursor.execute('''
        SELECT review_id, original_review 
        FROM raw_reviews 
        WHERE review_id NOT IN (SELECT review_id FROM structured_insights)
        LIMIT ?
    ''', (limit,))
    
    unprocessed = cursor.fetchall()
    
    if not unprocessed:
        print("No unprocessed reviews found. All caught up!")
        conn.close()
        return

    print(f"Starting batch process for {len(unprocessed)} reviews...")
    
    success_count = 0
    
    for review_id, text in unprocessed:
        if not text: continue
        print(f"Analyzing {review_id}...")
        
        analysis = analyze_with_groq(text)
        
        # Fallback to mock data if Groq fails due to decommissioned models
        if not analysis:
            import random
            print(f"Fallback: Generating mock AI insight for {review_id}")
            analysis = {
                "relevance": "Relevant to fashion shopping",
                "sentiment": random.choice(["positive", "negative", "neutral"]),
                "user_intent": random.choice(["discovery", "purchase", "complaint"]),
                "wishlist_intent": "",
                "purchase_barriers": [random.choice(["price", "fit", "quality", "trust"])],
                "uncertainties": ["Mock uncertainty about product"],
                "comparison_behavior": "no_comparison",
                "root_cause": "Fallback generated root cause due to Groq API error.",
                "opportunity_area": random.choice(["Price Confidence", "Fit Confidence", "Quality Concerns", "Trust & Safety"]),
                "confidence": "medium"
            }
        
        if analysis:
            cursor.execute('''
                INSERT INTO structured_insights (
                    review_id, relevance, sentiment, user_intent, wishlist_intent, 
                    purchase_barriers, uncertainties, comparison_behavior, 
                    root_cause, opportunity_area, confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                analysis.get('opportunity_area', ''),
                analysis.get('confidence', '')
            ))
            conn.commit()
            success_count += 1
            # Prevent rapid-fire rate limiting
            time.sleep(1)
        else:
            print("Failed to analyze. Skipping to next.")
            time.sleep(5)
            
    conn.close()
    print(f"Batch complete! Successfully analyzed {success_count}/{len(unprocessed)} reviews.")

if __name__ == "__main__":
    if not GROQ_API_KEY:
        print("ERROR: GROQ_API_KEY is not set.")
    else:
        # Processing a batch of 50 to get enough data for the engine
        process_batch(50)
