import sqlite3

def check_opportunities(db_path):
    print(f"Checking opportunities in {db_path}...")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check total rows
        count = cursor.execute("SELECT COUNT(*) FROM structured_insights").fetchone()[0]
        print(f"Total rows in structured_insights: {count}")
        
        # Check distinct opportunity_name
        cursor.execute("SELECT DISTINCT opportunity_name FROM structured_insights;")
        areas = cursor.fetchall()
        print('Distinct opportunity_name:', areas)
        
        # Check distinct values in root_cause, wishlist_intent
        cursor.execute("SELECT DISTINCT root_cause FROM structured_insights LIMIT 5;")
        print('Root causes:', cursor.fetchall())
        
        # See sample data
        cursor.execute("SELECT opportunity_name, root_cause, confidence, wishlist_intent FROM structured_insights LIMIT 5;")
        print('Sample 5 rows:', cursor.fetchall())
        
    except Exception as e:
        print("Error:", e)

check_opportunities('backend/myntra_discovery_basic.db')
