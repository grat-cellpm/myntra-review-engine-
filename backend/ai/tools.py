import sqlite3
import json
import os

DB_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "myntra_discovery_basic.db")

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def search_reviews(query: str = "", intent: str = "", barrier: str = "", limit: int = 10) -> str:
    """
    Search through raw reviews and structured insights based on keywords, user intent, or purchase barrier.
    Use this to find specific evidence or read what users are saying.
    """
    if not os.path.exists(DB_FILE):
        return "Database not found. No data available."
        
    conn = get_db_connection()
    
    sql = '''
        SELECT r.original_review, s.user_intent, s.opportunity_area, s.root_cause
        FROM raw_reviews r
        LEFT JOIN structured_insights s ON r.review_id = s.review_id
        WHERE 1=1
    '''
    params = []
    
    if query:
        sql += " AND (r.original_review LIKE ? OR s.root_cause LIKE ?)"
        params.extend([f"%{query}%", f"%{query}%"])
    if intent:
        sql += " AND s.user_intent LIKE ?"
        params.append(f"%{intent}%")
    if barrier:
        sql += " AND s.opportunity_area LIKE ?"
        params.append(f"%{barrier}%")
        
    sql += " LIMIT ?"
    params.append(min(limit, 5))
    
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    
    if not rows:
        return "No reviews found matching the criteria."
        
    results = []
    for idx, row in enumerate(rows):
        res = f"Review {idx+1}: '{row['original_review']}'"
        if row['user_intent']:
            res += f" | Intent: {row['user_intent']}"
        if row['opportunity_area']:
            res += f" | Barrier: {row['opportunity_area']}"
        if row['root_cause']:
            res += f" | Root Cause: {row['root_cause']}"
        results.append(res)
        
    return "\n".join(results)


def analyze_insight(opportunity_area: str) -> str:
    """
    Summarizes the common root causes and barriers associated with a specific opportunity area.
    Use this to dive deep into a particular problem area like 'Fit Confidence' or 'Price Confidence'.
    """
    if not os.path.exists(DB_FILE):
        return "Database not found. No data available."
        
    conn = get_db_connection()
    rows = conn.execute('''
        SELECT purchase_barriers, root_cause
        FROM structured_insights
        WHERE opportunity_area LIKE ?
    ''', (f"%{opportunity_area}%",)).fetchall()
    conn.close()
    
    if not rows:
        return f"No insights found for opportunity area: {opportunity_area}"
        
    barriers_set = set()
    root_causes = []
    
    for row in rows:
        if row['root_cause']:
            root_causes.append(row['root_cause'])
        try:
            barriers = json.loads(row['purchase_barriers'])
            if isinstance(barriers, list):
                barriers_set.update(barriers)
        except:
            pass
            
    summary = f"Analysis for '{opportunity_area}':\n"
    summary += f"- Found {len(rows)} related reviews.\n"
    summary += f"- Common Barriers: {', '.join(list(barriers_set)[:5])}\n"
    summary += f"- Sample Root Causes: {'; '.join(root_causes[:3])}\n"
    
    return summary


def compare_opportunities(area_1: str, area_2: str) -> str:
    """
    Compares the mention frequency of two different opportunity areas.
    Use this to help prioritize which problem to solve first.
    """
    if not os.path.exists(DB_FILE):
        return "Database not found."
        
    conn = get_db_connection()
    total = conn.execute('SELECT COUNT(*) FROM structured_insights WHERE opportunity_area != ""').fetchone()[0]
    
    count_1 = conn.execute('SELECT COUNT(*) FROM structured_insights WHERE opportunity_area LIKE ?', (f"%{area_1}%",)).fetchone()[0]
    count_2 = conn.execute('SELECT COUNT(*) FROM structured_insights WHERE opportunity_area LIKE ?', (f"%{area_2}%",)).fetchone()[0]
    conn.close()
    
    if total == 0:
        return "Not enough data to compare."
        
    pct_1 = round((count_1 / total) * 100, 1)
    pct_2 = round((count_2 / total) * 100, 1)
    
    result = f"Comparison:\n"
    result += f"- {area_1}: {count_1} mentions ({pct_1}% of all issues)\n"
    result += f"- {area_2}: {count_2} mentions ({pct_2}% of all issues)\n"
    
    if count_1 > count_2:
        result += f"Conclusion: '{area_1}' is mentioned more frequently."
    elif count_2 > count_1:
        result += f"Conclusion: '{area_2}' is mentioned more frequently."
    else:
        result += f"Conclusion: Both are mentioned with equal frequency."
        
    return result


def get_metrics() -> str:
    """
    Retrieves high-level dashboard statistics such as total reviews and common sentiment.
    """
    if not os.path.exists(DB_FILE):
        return "Database not found."
        
    conn = get_db_connection()
    total_reviews = conn.execute('SELECT COUNT(*) FROM raw_reviews').fetchone()[0]
    total_analyzed = conn.execute('SELECT COUNT(*) FROM structured_insights').fetchone()[0]
    
    # Just a simple top 3 barriers
    top_barriers = conn.execute('''
        SELECT opportunity_area, COUNT(*) as cnt 
        FROM structured_insights 
        WHERE opportunity_area != "" AND opportunity_area IS NOT NULL
        GROUP BY opportunity_area 
        ORDER BY cnt DESC 
        LIMIT 3
    ''').fetchall()
    
    conn.close()
    
    res = f"Overall Metrics:\n- Total Collected Reviews: {total_reviews}\n- Total Analyzed by AI: {total_analyzed}\n"
    res += "- Top 3 Opportunity Areas:\n"
    for b in top_barriers:
        res += f"  * {b['opportunity_area']} ({b['cnt']} mentions)\n"
        
    return res


def generate_report(findings: str) -> str:
    """
    Formats the gathered findings into a structured report. 
    Use this tool as the LAST step to format the answer properly.
    """
    return f"REPORT GENERATED SUCCESSFULLY.\n\n{findings}"

def semantic_search_reviews(query: str, limit: int = 5) -> str:
    """
    Uses Retrieval-Augmented Generation (RAG) to find reviews that are semantically related to the query.
    Use this when exact keyword searches fail, or when the user asks a conceptual question (e.g. 'what are people saying about the fabric?').
    """
    try:
        from database.vector_store import vector_store
        results = vector_store.search(query, limit=min(limit, 5))
        
        if not results:
            return "No semantically related reviews found in the vector database."
            
        formatted = []
        for i, res in enumerate(results):
            score = round(res['score'], 3)
            doc = res['document'].replace('\n', ' | ')
            formatted.append(f"Result {i+1} (Score: {score}): {doc}")
            
        return "\n".join(formatted)
    except Exception as e:
        return f"Semantic search failed: {str(e)}"
