import sqlite3, os
db_path = r'c:\Users\ASUS\OneDrive\Desktop\Myntra R\backend\myntra_discovery_basic.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()
c.execute('DROP TABLE IF EXISTS structured_insights')
c.execute('''
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
    confidence TEXT
)
''')
c.execute('DROP TABLE IF EXISTS raw_reviews')
c.execute('''
CREATE TABLE raw_reviews (
    review_id TEXT PRIMARY KEY,
    product_name TEXT,
    rating INTEGER,
    original_review TEXT,
    author_identifier TEXT,
    timestamp TEXT,
    source TEXT
)
''')

# Insert enough mock raw reviews to create the desired percentages out of 500
# Fit & Size Uncertainty (24% of 500 = 120 reviews) -> We don't actually need to insert 120 rows, just enough mentions and adjust total_analyzed in app.py or we can mock the frequency in the UI? 
# Wait, the UI relies on mention_count / total_analyzed. But total_analyzed is currently SELECT COUNT(*) FROM structured_insights.
# If I just insert the exact mentions to get those percentages:
# If total insights = 100, then 24 mentions = 24%.
# But total_analyzed in app.py is COUNT(*) of structured_insights.
# Let's insert a fixed number of rows:
# Fit: 24
# Product: 17
# Choice: 13
# Price: 10
# Total so far = 64. Let's add 36 "Other" to make it 100. Then percentages will match exactly.

# First, insert raw reviews
for i in range(1, 101):
    c.execute('INSERT INTO raw_reviews (review_id, product_name, rating, original_review, author_identifier, timestamp, source) VALUES (?, ?, ?, ?, ?, "", "")', 
              (f'r{i}', 'Product', 3, 'This is a mock review.', f'User {i}'))

# Insert opportunities
def insert_opps(start, count, name, desc, score, wl):
    for i in range(start, start + count):
        c.execute('INSERT INTO structured_insights (review_id, opportunity_name, opportunity_description, customer_impact_score, wishlist_to_purchase_impact) VALUES (?, ?, ?, ?, ?)', 
                  (f'r{i}', name, desc, score, wl))

insert_opps(1, 24, 'Fit & Size Uncertainty', 'Users are uncertain whether the product will fit correctly, causing them to abandon purchases.', 9, 'High')
insert_opps(25, 17, 'Product Information Gap', 'Product descriptions lack critical details like material feel or exact dimensions.', 8, 'High')
insert_opps(42, 13, 'Choice Overload', 'Customers are overwhelmed by too many visually similar options without clear differences.', 6, 'Medium')
insert_opps(55, 10, 'Price Hesitation', 'Users find the item appealing but hesitate because they perceive the price as slightly too high without a discount.', 5, 'Medium')
insert_opps(65, 36, 'Other Miscellaneous', 'Various minor issues.', 2, 'Low')

conn.commit()
conn.close()
print('Mock data updated to match wireframe!')
