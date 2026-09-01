import sqlite3
import json

def test_logic():
    conn = sqlite3.connect('backend/myntra_discovery_basic.db')
    
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
    
    opps_dict = {}
    for row in rows:
        raw_name, desc, confidence, wl_intent, rev_text, rating, author = row
        
        if not raw_name or str(raw_name).lower() == "none" or str(raw_name).lower() == "null" or str(raw_name).strip() == "":
            continue
            
        opp = str(raw_name).strip().title()
        
        if opp not in opps_dict:
            opps_dict[opp] = {
                "opportunity": opp,
                "description": desc or "",
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
        priority_score = round(freq / 2.0, 1)
        
        if priority_score > 8: priority_level = "Critical"
        elif priority_score > 4: priority_level = "High"
        elif priority_score > 2: priority_level = "Medium"
        else: priority_level = "Low"
            
        wl_impact = "Medium"
        if v["wishlist_intents"]:
            wl_impact = max(set(v["wishlist_intents"]), key=v["wishlist_intents"].count)
            
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
    
    print("Result size:", len(result))
    if len(result) > 0:
        print(json.dumps(result[0], indent=2))

test_logic()
