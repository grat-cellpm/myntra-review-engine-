import os
import json
from pydantic import BaseModel, Field
from typing import List, Optional
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Pydantic schema for structured output
class StructuredReviewAnalysis(BaseModel):
    relevance: str = Field(description="Relevant to fashion shopping, Not relevant, Unclear")
    sentiment: str = Field(description="positive, neutral, negative, mixed")
    user_intent: str = Field(description="discovery, consideration, wishlist, purchase, postponed_purchase, comparison, alternative_search, complaint, return")
    wishlist_intent: str = Field(description="genuine_purchase_intent, save_for_later, bookmarking, price_watch, comparison_shortlist, inspiration")
    purchase_barriers: List[str] = Field(description="price, fit_size, quality, trust, lack_of_information, decision_overload, availability")
    uncertainties: List[str] = Field(description="List of unresolved questions in the user's mind")
    comparison_behavior: str = Field(description="comparing_products, comparing_brands, comparing_prices, comparing_features, comparing_styles, no_comparison")
    alternative_found: bool = Field(description="Whether the user found an alternative product")
    root_cause: str = Field(description="Inferred underlying reason behind the behavior")
    opportunity_area: str = Field(description="price_value, fit_size, product_confidence, reviews_social_validation, product_comparison, styling_occasion, purchase_timing_reengagement, alternative_discovery")
    confidence: str = Field(description="high, medium, low")


class GroqEngine:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "openai/gpt-oss-20b" # Choose appropriate groq model
        
    def analyze_review(self, review_text: str) -> Optional[StructuredReviewAnalysis]:
        prompt = f"""
        Analyze the following user review or comment about an online fashion shopping platform (like Myntra).
        Extract structured insights according to the JSON schema provided.
        
        To arrive at your conclusion, determine the answers to these questions in this exact order:
        1. Which theme?
        2. What behavior?
        3. What is the barrier?
        4. What uncertainty exists?
        5. What is the root cause?
        6. What opportunity does it indicate?
        
        Review:
        "{review_text}"
        """
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI user research assistant analyzing fashion e-commerce reviews. You extract structured insights by following a strict logical sequence."
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.model,
                temperature=0,
                response_format={"type": "json_object"}
            )
            
            response_json_str = chat_completion.choices[0].message.content
            # Validate with Pydantic
            analysis = StructuredReviewAnalysis.model_validate_json(response_json_str)
            return analysis
            
        except Exception as e:
            print(f"Error analyzing review with Groq: {e}")
            return None
