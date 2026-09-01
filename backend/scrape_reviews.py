import sqlite3
from google_play_scraper import reviews, Sort

DB_FILE = "myntra_discovery_basic.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS raw_reviews (
            review_id TEXT PRIMARY KEY,
            source TEXT,
            original_review TEXT,
            rating REAL,
            review_date TEXT,
            author_identifier TEXT
        )
    ''')
    conn.commit()
    conn.close()

def fetch_and_save_reviews(limit=1000):
    print(f"Fetching {limit} reviews from Google Play Store... This may take a moment.")
    try:
        result, _ = reviews(
            "com.myntra.android",
            lang='en',
            country='in',
            sort=Sort.NEWEST,
            count=limit
        )
    except Exception as e:
        print(f"Failed to fetch reviews: {e}")
        return

    print(f"Successfully fetched {len(result)} reviews. Saving to database...")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    saved_count = 0
    skipped_count = 0
    
    for item in result:
        review_id = item.get('reviewId')
        content = item.get('content')
        rating = item.get('score')
        date_str = str(item.get('at'))
        author = item.get('userName')
        
        try:
            cursor.execute('''
                INSERT INTO raw_reviews (review_id, source, original_review, rating, review_date, author_identifier)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (review_id, 'google_play', content, rating, date_str, author))
            saved_count += 1
        except sqlite3.IntegrityError:
            skipped_count += 1
            
    conn.commit()
    conn.close()
    
    print(f"Done! Saved {saved_count} new reviews. Skipped {skipped_count} duplicates.")

if __name__ == "__main__":
    init_db()
    fetch_and_save_reviews(1000)
