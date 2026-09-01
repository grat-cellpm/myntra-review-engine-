import os
import praw
from typing import List
from datetime import datetime
from .base import BaseCollector

class RedditCollector(BaseCollector):
    
    def __init__(self, subreddit_name: str = "IndianFashionAddicts"):
        self.subreddit_name = subreddit_name
        
        # Ensure these are in .env
        client_id = os.getenv("REDDIT_CLIENT_ID")
        client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        user_agent = os.getenv("REDDIT_USER_AGENT", "MyntraResearchBot/0.1")
        
        self.reddit = None
        if client_id and client_secret:
            self.reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent
            )
            
    @property
    def source_name(self) -> str:
        return "reddit"
        
    def fetch_reviews(self, limit: int = 100) -> List[dict]:
        if not self.reddit:
            print("Reddit credentials not found. Skipping Reddit collection.")
            return []
            
        subreddit = self.reddit.subreddit(self.subreddit_name)
        
        # Searching for 'myntra' in the subreddit
        search_results = subreddit.search("myntra", sort="new", limit=limit)
        
        formatted_data = []
        for submission in search_results:
            full_text = f"{submission.title}\n{submission.selftext}"
            
            formatted_data.append({
                "review_id": f"t3_{submission.id}",
                "source_url": f"https://reddit.com{submission.permalink}",
                "original_review": full_text,
                "rating": None, # Reddit doesn't have 1-5 ratings
                "review_date": datetime.fromtimestamp(submission.created_utc),
                "language": "en",
                "country": "in",
                "app_version": None,
                "author_identifier": str(submission.author) if submission.author else "[deleted]"
            })
            
            # We could also fetch comments here, but for MVP let's stick to submissions
            
        return formatted_data
