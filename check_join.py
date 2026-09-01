import sqlite3

def check_join():
    conn = sqlite3.connect('backend/myntra_discovery_basic.db')
    
    # Total structured_insights
    print("Total insights:", conn.execute("SELECT COUNT(*) FROM structured_insights").fetchone()[0])
    
    # Try the join
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
    
    print("Join rows:", len(rows))
    
    if len(rows) == 0:
        # Check review_id in both
        print("s.review_id sample:", conn.execute("SELECT review_id FROM structured_insights LIMIT 3").fetchall())
        print("r.review_id sample:", conn.execute("SELECT review_id FROM raw_reviews LIMIT 3").fetchall())

check_join()
