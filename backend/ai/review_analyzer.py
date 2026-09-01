import os
import json
from pydantic import BaseModel, Field
from typing import List, Optional
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class ProductReviewScore(BaseModel):
    quality_score: float = Field(description="Score from 1.0 to 10.0 based on depth of information and usefulness.")
    authenticity_confidence: float = Field(description="Score from 1.0 to 10.0 based on natural language vs bot-like patterns.")

class ProductInsightExtraction(BaseModel):
    fit_size: Optional[str] = Field(description="Insights regarding fit or size. Leave null if not mentioned.")
    fabric_comfort: Optional[str] = Field(description="Insights regarding fabric or comfort. Leave null if not mentioned.")
    quality_durability: Optional[str] = Field(description="Insights regarding quality or durability. Leave null if not mentioned.")
    color_accuracy: Optional[str] = Field(description="Insights regarding color matching expectations. Leave null if not mentioned.")
    price_value: Optional[str] = Field(description="Insights regarding price vs value. Leave null if not mentioned.")
    actual_usage: Optional[str] = Field(description="Context of how the user actually used the product. Leave null if not mentioned.")

class ReviewAnalyzer:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        # Using a reliable model, llama-3.1-8b-instant or 70b
        self.model = "llama-3.1-8b-instant" 

    def score_review(self, review_text: str) -> Optional[ProductReviewScore]:
        prompt = f"""
        Analyze this product review and score it on two metrics from 1 to 10.
        1. Quality Score: How detailed, specific, and useful is this review?
        2. Authenticity Confidence: Does this look like a real human wrote it (high score) or is it repetitive/bot-like (low score)?
        
        Review: "{review_text}"
        """
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a JSON-only API for scoring reviews."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0,
                response_format={"type": "json_object"}
            )
            response_json_str = chat_completion.choices[0].message.content
            return ProductReviewScore.model_validate_json(response_json_str)
        except Exception as e:
            print(f"Error scoring review: {e}")
            return None

    def extract_insights(self, review_text: str) -> Optional[ProductInsightExtraction]:
        prompt = f"""
        Extract specific insights from the following product review for the specified categories. 
        If a category is not mentioned in the review, return null for that category.
        Do not make up information.
        
        Review: "{review_text}"
        """
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a JSON-only API for extracting product insights."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0,
                response_format={"type": "json_object"}
            )
            response_json_str = chat_completion.choices[0].message.content
            return ProductInsightExtraction.model_validate_json(response_json_str)
        except Exception as e:
            print(f"Error extracting insights: {e}")
            return None

    def generate_summary(self, product_id: str, reviews: list[dict], insights: list[dict]) -> tuple[str, list]:
        """
        Generates a summary based on the provided reviews and their extracted insights.
        Returns a tuple of (markdown_summary, themes_json)
        """
        # Truncate to a sample if there are too many for the context window
        sample_size = min(len(reviews), 50) 
        sample_reviews = reviews[:sample_size]
        
        reviews_context = "\n".join([f"- {r.get('original_review', '')}" for r in sample_reviews])
        
        prompt = f"""
        You are an expert user researcher. Analyze these {sample_size} product reviews and their extracted insights.
        
        1. Identify the recurring themes and customer pain points.
        2. Write a markdown-formatted summary of the findings.
        3. For each major insight in your summary, you MUST include 1-2 exact, verbatim quotes from the reviews provided below to support it. Do NOT fabricate quotes.
        4. Also provide a JSON array of the top themes and the approximate percentage of reviews they appear in.
        
        Format your response as a JSON object with two keys:
        - "summary_markdown": the markdown text string
        - "themes": an array of objects like [{{"theme": "Fit is too small", "percentage": 40}}]
        
        Reviews to analyze:
        {reviews_context}
        """
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a JSON-only API for summarizing product reviews."},
                    {"role": "user", "content": prompt}
                ],
                model="llama-3.1-70b-versatile", # Use a larger model for synthesis
                temperature=0,
                response_format={"type": "json_object"}
            )
            response_json_str = chat_completion.choices[0].message.content
            data = json.loads(response_json_str)
            return data.get("summary_markdown", ""), data.get("themes", [])
        except Exception as e:
            print(f"Error generating summary: {e}")
            return "", []
