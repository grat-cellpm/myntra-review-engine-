import sys
import os
import sqlite3

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.vector_store import vector_store

def build_vector_db():
    print("Building Vector Database...")
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'myntra_discovery_basic.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    
    # Get all reviews and their insights
    reviews = conn.execute('''
        SELECT r.review_id, r.original_review, r.source, r.rating,
               s.user_intent, s.sentiment, s.purchase_barriers, 
               s.opportunity_name, s.opportunity_description, s.root_cause
        FROM raw_reviews r
        LEFT JOIN structured_insights s ON r.review_id = s.review_id
    ''').fetchall()
    
    documents = []
    ids = []
    metadatas = []
    
    print(f"Found {len(reviews)} reviews. Embedding into FastEmbed...")
    
    for row in reviews:
        # Create a cohesive string for semantic search
        doc = f"Review Text: {row['original_review']}\n"
        
        meta = {
            "source": row['source'] or "unknown",
            "rating": float(row['rating'] or 0.0)
        }
        
        if row['user_intent'] is not None:
            doc += f"User Intent: {row['user_intent'] or 'N/A'}\n"
            doc += f"Sentiment: {row['sentiment'] or 'N/A'}\n"
            doc += f"Purchase Barriers: {row['purchase_barriers'] or 'N/A'}\n"
            doc += f"Opportunity: {row['opportunity_name'] or 'N/A'} - {row['opportunity_description'] or 'N/A'}\n"
            doc += f"Root Cause: {row['root_cause'] or 'N/A'}\n"
            
            meta["sentiment"] = row['sentiment'] or "unknown"
            meta["opportunity_area"] = row['opportunity_name'] or "unknown"
            
        documents.append(doc)
        ids.append(row['review_id'])
        metadatas.append(meta)
        
    # Batch upsert
    batch_size = 100
    for i in range(0, len(documents), batch_size):
        vector_store.upsert(
            documents=documents[i:i+batch_size],
            metadatas=metadatas[i:i+batch_size],
            ids=ids[i:i+batch_size]
        )
        print(f"Upserted {i + len(documents[i:i+batch_size])} / {len(documents)}")
        
    print("Vector Database build complete!")
    conn.close()

if __name__ == "__main__":
    build_vector_db()
