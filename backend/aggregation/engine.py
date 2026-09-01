from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
from database.models import StructuredInsight

class AggregationEngine:
    
    @staticmethod
    def get_opportunity_stats(db: Session) -> List[Dict[str, Any]]:
        """
        Calculates stats for each opportunity area.
        Returns a list of dictionaries with opportunity name, mention count, and scores.
        """
        # Get total relevant reviews for percentage calculation
        total_relevant = db.query(StructuredInsight).filter(
            StructuredInsight.relevance == "Relevant to fashion shopping"
        ).count()
        
        if total_relevant == 0:
            return []
            
        # Group by opportunity area
        opportunities = db.query(
            StructuredInsight.opportunity_area,
            func.count(StructuredInsight.id).label("mention_count")
        ).filter(
            StructuredInsight.relevance == "Relevant to fashion shopping"
        ).group_by(
            StructuredInsight.opportunity_area
        ).all()
        
        results = []
        for opp in opportunities:
            opp_name = opp.opportunity_area
            mention_count = opp.mention_count
            percentage = (mention_count / total_relevant) * 100
            
            # Basic dummy scoring logic for MVP, replace with real weights and logic
            # Frequency: 30%, User Impact: 25%, Purchase Relevance: 30%, Evidence Strength: 15%
            # For MVP, we'll derive a simple score based largely on frequency and a random component
            # In a real app, impact and relevance might be derived from specific intents/barriers
            frequency_score = min(percentage / 50 * 10, 10) # Max 10 if 50% or more mentions
            
            score = round((frequency_score * 0.3) + (8 * 0.25) + (9 * 0.3) + (7 * 0.15), 1)
            
            results.append({
                "opportunity": opp_name,
                "frequency_percentage": round(percentage, 1),
                "mention_count": mention_count,
                "impact": "High" if percentage > 15 else ("Medium" if percentage > 5 else "Low"),
                "relevance": "High", # Assuming all extracted opportunities are high relevance
                "score": min(score, 10.0)
            })
            
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
        
    @staticmethod
    def get_dashboard_overview(db: Session) -> Dict[str, Any]:
        """
        Get high-level dashboard metrics.
        """
        total_analyzed = db.query(StructuredInsight).count()
        total_relevant = db.query(StructuredInsight).filter(
            StructuredInsight.relevance == "Relevant to fashion shopping"
        ).count()
        
        top_opportunities = AggregationEngine.get_opportunity_stats(db)[:5]
        
        return {
            "total_analyzed": total_analyzed,
            "relevant_reviews": total_relevant,
            "top_opportunities": top_opportunities
        }
