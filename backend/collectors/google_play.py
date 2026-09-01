import uuid
from typing import List
from datetime import datetime
from google_play_scraper import reviews, Sort
from .base import BaseCollector

class GooglePlayCollector(BaseCollector):
    
    def __init__(self, app_id: str = "com.myntra.android"):
        self.app_id = app_id
        
    @property
    def source_name(self) -> str:
        return "google_play"
        
    def fetch_reviews(self, limit: int = 100) -> List[dict]:
        result, continuation_token = reviews(
            self.app_id,
            lang='en', # defaults to 'en'
            country='in', # defaults to 'us'
            sort=Sort.NEWEST, # defaults to Sort.NEWEST
            count=limit
        )
        
        formatted_data = []
        for item in result:
            formatted_data.append({
                "review_id": item.get('reviewId'),
                "source_url": f"https://play.google.com/store/apps/details?id={self.app_id}&reviewId={item.get('reviewId')}",
                "original_review": item.get('content'),
                "rating": float(item.get('score')) if item.get('score') else None,
                "review_date": item.get('at'), # is already a datetime object
                "language": 'en',
                "country": 'in',
                "app_version": item.get('reviewCreatedVersion'),
                "author_identifier": item.get('userName')
            })
            
        return formatted_data
