import re
from typing import List
from database.models import RawReview
import langid

class DataCleaner:
    
    @staticmethod
    def clean_text(text: str) -> str:
        if not text:
            return ""
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    @staticmethod
    def detect_language(text: str) -> str:
        if not text:
            return "unknown"
        try:
            lang, _ = langid.classify(text)
            return lang
        except Exception:
            return "unknown"

    @staticmethod
    def filter_and_clean(reviews: List[RawReview]) -> List[RawReview]:
        """
        Takes a list of RawReview models, cleans text, detects language, 
        and removes obvious spam or exact duplicates based on review_id.
        """
        seen_ids = set()
        cleaned_reviews = []
        
        for review in reviews:
            if review.review_id in seen_ids:
                continue
            seen_ids.add(review.review_id)
            
            # Clean text
            review.original_review = DataCleaner.clean_text(review.original_review)
            
            # Very basic spam detection - skip empty reviews or extremely short ones
            if not review.original_review or len(review.original_review.split()) < 4 or len(review.original_review) < 20:
                continue
                
            # If language wasn't provided by the collector, detect it
            if not review.language or review.language == "unknown":
                review.language = DataCleaner.detect_language(review.original_review)
                
            cleaned_reviews.append(review)
            
        return cleaned_reviews
