from flask import Flask, jsonify
from flask_cors import CORS
import sqlite3
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes so Next.js can fetch data

DB_FILE = os.path.join(os.path.dirname(__file__), "myntra_discovery_basic.db")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/health')
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/api/reviews')
def get_reviews():
    if not os.path.exists(DB_FILE):
        return jsonify([])
        
    conn = get_db_connection()
    # Left join to get structured insights if they exist (even if Groq failed, we at least have raw_reviews)
    reviews = conn.execute('''
        SELECT r.review_id, r.source, r.original_review, r.rating, r.review_date, r.author_identifier,
               s.relevance, s.sentiment, s.user_intent, s.wishlist_intent, s.opportunity_name as opportunity_area
        FROM raw_reviews r
        LEFT JOIN structured_insights s ON r.review_id = s.review_id
        ORDER BY r.review_date DESC
    ''').fetchall()
    conn.close()
    
    # Convert sqlite3.Row objects to dicts
    result = []
    for row in reviews:
        text = row["original_review"] or ""
        # Filter out short one-liners and generic reviews (e.g. "everything is good")
        if len(text.split()) < 10 or len(text) < 50:
            continue
            
        # Handling the case where Groq AI failed, so sentiment might be null
        sentiment = row['sentiment'] if row['sentiment'] else 'Pending Analysis'
        intent = row['user_intent'] if row['user_intent'] else 'Unknown'
        # Assuming barrier_text or opportunity_area is the barrier
        barrier = row['opportunity_area'] if row['opportunity_area'] else 'None'
        
        result.append({
            "id": row["review_id"],
            "rating": row["rating"],
            "text": row["original_review"],
            "sentiment": sentiment,
            "intent": intent,
            "barrier": barrier,
            "source": row["source"],
            "date": row["review_date"],
            "author": row["author_identifier"]
        })
        
    return jsonify(result)

@app.route('/api/dashboard-stats')
def get_dashboard_stats():
    if not os.path.exists(DB_FILE):
        return jsonify({})

    conn = get_db_connection()
    raw_reviews = conn.execute('SELECT original_review, rating FROM raw_reviews').fetchall()
    total_analyzed_row = conn.execute('SELECT COUNT(*) FROM structured_insights').fetchone()
    total_analyzed = total_analyzed_row[0] if total_analyzed_row else 0
    conn.close()

    total_reviews = len(raw_reviews)
    
    # Heuristics
    sentiment_counts = {"Positive": 0, "Neutral": 0, "Negative": 0}
    barrier_counts = {"Price": 0, "Fit": 0, "Trust": 0, "Quality": 0, "Other": 0}
    
    positive_words = ['good', 'great', 'love', 'perfect', 'awesome', 'nice', 'best', 'amazing']
    negative_words = ['bad', 'worst', 'hate', 'terrible', 'awful', 'poor', 'disappointed', 'issue']
    
    price_words = ['price', 'expensive', 'cost', 'money', 'cheap']
    fit_words = ['size', 'fit', 'small', 'large', 'tight', 'loose']
    trust_words = ['fake', 'scam', 'fraud', 'trust', 'customer service', 'support']
    quality_words = ['material', 'fabric', 'torn', 'break', 'quality', 'color']

    for row in raw_reviews:
        text = row['original_review'].lower() if row['original_review'] else ""
        rating = row['rating']
        
        # Sentiment logic
        if rating >= 4 or any(w in text for w in positive_words):
            sentiment_counts["Positive"] += 1
        elif rating <= 2 or any(w in text for w in negative_words):
            sentiment_counts["Negative"] += 1
        else:
            sentiment_counts["Neutral"] += 1
            
        # Barrier logic
        if any(w in text for w in price_words): 
            barrier_counts["Price"] += 1
        elif any(w in text for w in fit_words): 
            barrier_counts["Fit"] += 1
        elif any(w in text for w in trust_words): 
            barrier_counts["Trust"] += 1
        elif any(w in text for w in quality_words): 
            barrier_counts["Quality"] += 1
        else:
            barrier_counts["Other"] += 1

    # Format for frontend Recharts
    sentiment_breakdown = [
        {"name": "Positive", "value": round((sentiment_counts["Positive"] / total_reviews) * 100) if total_reviews else 0, "color": "#4f46e5"},
        {"name": "Neutral", "value": round((sentiment_counts["Neutral"] / total_reviews) * 100) if total_reviews else 0, "color": "#a855f7"},
        {"name": "Negative", "value": round((sentiment_counts["Negative"] / total_reviews) * 100) if total_reviews else 0, "color": "#2563eb"}
    ]
    
    top_barriers = [
        {"name": "Price", "value": barrier_counts["Price"]},
        {"name": "Fit", "value": barrier_counts["Fit"]},
        {"name": "Trust", "value": barrier_counts["Trust"]},
        {"name": "Quality", "value": barrier_counts["Quality"]},
        {"name": "Other", "value": barrier_counts["Other"]},
    ]
    
    # Sort barriers descending
    top_barriers = sorted(top_barriers, key=lambda x: x['value'], reverse=True)
    
    wishlist_breakdown = [
        {"name": "Price Watch", "value": 40, "color": "#10b981"},
        {"name": "Comparison Shortlist", "value": 30, "color": "#3b82f6"},
        {"name": "Genuine Intent", "value": 20, "color": "#8b5cf6"},
        {"name": "Inspiration", "value": 10, "color": "#f59e0b"}
    ]

    return jsonify({
        "totalReviews": total_reviews,
        "totalAnalyzed": total_analyzed,
        "highImpactOpportunities": sum(1 for b in barrier_counts.values() if b > 20),
        "avgFitScore": 6.8, # Mocked complex score for now
        "sentimentBreakdown": sentiment_breakdown,
        "wishlistBreakdown": wishlist_breakdown,
        "topBarriers": top_barriers
    })

@app.route('/api/opportunities')
def get_opportunities():
    if not os.path.exists(DB_FILE): return jsonify([])
    conn = get_db_connection()
    
    opps_dict = {}
    rows = conn.execute('''
        SELECT 
            s.opportunity_name as opportunity_area,
            s.root_cause as description,
            s.confidence,
            s.wishlist_intent,
            r.original_review,
            r.rating,
            r.author_identifier
        FROM structured_insights s
        JOIN raw_reviews r ON s.review_id = r.review_id
    ''').fetchall()
    
    total_analyzed = conn.execute('SELECT COUNT(*) FROM structured_insights').fetchone()[0]
    conn.close()
    
    if total_analyzed == 0:
        return jsonify([])
        
    for row in rows:
        raw_name, desc, confidence, wl_intent, rev_text, rating, author = row
        
        if not raw_name or str(raw_name).lower() == "none" or str(raw_name).lower() == "null" or str(raw_name).strip() == "":
            continue
            
        raw_opp = str(raw_name).strip().lower()
        desc_lower = str(desc).strip().lower()
        combined = raw_opp + " " + desc_lower
        
        # Categorize into the 7 requested buckets based on keywords
        opp = "Purchase Uncertainty" # Default
        
        if any(w in combined for w in ["price", "cost", "expensive", "value", "offer", "discount", "sale"]):
            opp = "Price & Value Hesitation"
        elif any(w in combined for w in ["fit", "size", "measurement", "too big", "too small", "tight", "loose"]):
            opp = "Fit & Size Confidence"
        elif any(w in combined for w in ["delivery", "shipping", "logistics", "return", "refund", "stock", "availability", "late", "delay", "support", "customer service"]):
            opp = "Availability & Purchase Friction"
        elif any(w in combined for w in ["trust", "authentic", "genuine", "information", "detail", "fake", "quality", "material"]):
            opp = "Information & Trust Gaps"
        elif any(w in combined for w in ["compare", "choice", "options", "filter", "search"]):
            opp = "Choice & Comparison Overload"
        elif any(w in combined for w in ["wishlist overload", "priority", "save for later", "too many"]):
            opp = "Wishlist Overload & Prioritization"
            
        # Optional: override description to use the user's defined descriptions for the buckets
        bucket_descriptions = {
            "Purchase Uncertainty": "User wants the product but lacks confidence to buy.",
            "Price & Value Hesitation": "User is waiting for a better price or is unsure about value.",
            "Choice & Comparison Overload": "User is comparing too many options and cannot decide.",
            "Information & Trust Gaps": "User needs more reliable information before purchasing.",
            "Fit & Size Confidence": "User is unsure whether the product will fit.",
            "Availability & Purchase Friction": "Size/stock, delivery, returns, or checkout create barriers.",
            "Wishlist Overload & Prioritization": "Users save many products and struggle to decide what to buy."
        }
        
        display_desc = bucket_descriptions.get(opp, desc)
        
        if opp not in opps_dict:
            opps_dict[opp] = {
                "opportunity": opp,
                "description": display_desc or "",
                "count": 0,
                "wishlist_intents": [],
                "evidence": []
            }
            
        opps_dict[opp]["count"] += 1
        
        if wl_intent:
            opps_dict[opp]["wishlist_intents"].append(wl_intent)
            
        if len(opps_dict[opp]["evidence"]) < 5 and rev_text:
            opps_dict[opp]["evidence"].append({
                "text": rev_text,
                "rating": rating,
                "author": author or "Anonymous"
            })
            
    result = []
    for k, v in opps_dict.items():
        freq = round((v["count"] / total_analyzed) * 100) if total_analyzed else 0
        
        # Determine Priority Score based on frequency for MVP
        priority_score = round(freq / 2.0, 1)
        
        if priority_score > 8:
            priority_level = "Critical"
        elif priority_score > 4:
            priority_level = "High"
        elif priority_score > 2:
            priority_level = "Medium"
        else:
            priority_level = "Low"
            
        wl_impact = "Medium"
        if v["wishlist_intents"]:
            wl_impact = max(set(v["wishlist_intents"]), key=v["wishlist_intents"].count)
            
        # Only include meaningful opportunities
        if v["count"] >= 1:
            result.append({
                "opportunity": v["opportunity"],
                "description": v["description"] if v["description"] else f"Users are experiencing friction related to {v['opportunity'].lower()}.",
                "frequency_percentage": freq,
                "mention_count": v["count"],
                "impact_score": priority_score,
                "priority_score": priority_score,
                "priority_level": priority_level,
                "wishlist_to_purchase_impact": wl_impact,
                "evidence": v["evidence"]
            })
        
    result = sorted(result, key=lambda x: x['priority_score'], reverse=True)
    return jsonify(result)

from flask import request

from ai.agent import Agent

@app.route('/api/agent/query', methods=['POST'])
def query_agent():
    print("API /agent/query HIT!", flush=True)
    if not GROQ_API_KEY:
        print("NO GROQ API KEY", flush=True)
        return jsonify({"error": "GROQ_API_KEY not configured"}), 500
        
    data = request.json
    question = data.get("question", "")
    print(f"QUESTION: {question}", flush=True)
    if not question:
        return jsonify({"error": "Question is required"}), 400
        
    try:
        agent = Agent(api_key=GROQ_API_KEY)
        print("AGENT INITIALIZED", flush=True)
        answer = agent.run(question)
        print("AGENT FINISHED", flush=True)
        return jsonify({"answer": answer})
    except Exception as e:
        print(f"AGENT ERROR: {e}", flush=True)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
