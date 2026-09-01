import sqlite3

def check_opportunities(db_path):
    print(f"Checking opportunities in {db_path}...")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT opportunity_area FROM structured_insights;")
        areas = cursor.fetchall()
        print('Distinct Opportunity Areas:', areas)
        cursor.execute("SELECT opportunity_area, COUNT(*) FROM structured_insights GROUP BY opportunity_area;")
        counts = cursor.fetchall()
        print('Counts:', counts)
    except Exception as e:
        print("Error:", e)

check_opportunities('backend/myntra_discovery_basic.db')
