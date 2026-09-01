import difflib

class ReviewFilter:
    def __init__(self, similarity_threshold=0.9, min_words=10):
        self.similarity_threshold = similarity_threshold
        self.min_words = min_words

    def is_generic_or_short(self, text: str) -> bool:
        if not text:
            return True
        words = text.split()
        if len(words) < self.min_words:
            return True
        
        # Check against some common generic templates
        generic_phrases = ["very good product", "nice product", "good quality", "awesome", "loved it", "superb"]
        lower_text = text.lower().strip()
        if lower_text in generic_phrases:
            return True
            
        return False

    def process_reviews(self, reviews: list[dict]) -> list[dict]:
        """
        Takes a list of review dicts (must have 'original_review' key).
        Returns a filtered and deduplicated list.
        """
        filtered = []
        seen_exact = set()
        
        for review in reviews:
            text = review.get('original_review', '')
            
            # 1. Check if generic or too short
            if self.is_generic_or_short(text):
                continue
                
            # 2. Exact duplicate check
            lower_text = text.lower().strip()
            if lower_text in seen_exact:
                continue
                
            # 3. Near-duplicate check against already accepted
            is_near_dup = False
            for accepted in filtered:
                accepted_text = accepted.get('original_review', '').lower().strip()
                similarity = difflib.SequenceMatcher(None, lower_text, accepted_text).ratio()
                if similarity >= self.similarity_threshold:
                    is_near_dup = True
                    break
                    
            if not is_near_dup:
                seen_exact.add(lower_text)
                filtered.append(review)
                
        return filtered
