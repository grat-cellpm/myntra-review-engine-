import requests
from typing import List
from datetime import datetime
from .base import BaseCollector
import uuid

class AppStoreCollector(BaseCollector):
    
    def __init__(self, app_id: str = "907394059", country: str = "in"):
        # Myntra app id: 907394059
        self.app_id = app_id
        self.country = country
        
    @property
    def source_name(self) -> str:
        return "app_store"
        
    def fetch_reviews(self, limit: int = 100) -> List[dict]:
        # Using the standard RSS feed for app store reviews
        # Note: This has limitations on count, usually ~50 per page, up to 10 pages.
        url = f"https://itunes.apple.com/{self.country}/rss/customerreviews/page=1/id={self.app_id}/sortby=mostrecent/json"
        
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error fetching App Store reviews: {response.status_code}")
            return []
            
        data = response.json()
        entries = data.get('feed', {}).get('entry', [])
        
        # The first entry is usually information about the app itself
        if entries and 'author' in entries[0] and 'uri' in entries[0].get('author', {}):
            entries = entries[1:]
            
        formatted_data = []
        for i, item in enumerate(entries):
            if i >= limit:
                break
                
            review_id = item.get('id', {}).get('label', str(uuid.uuid4()))
            content = item.get('content', {}).get('label', '')
            title = item.get('title', {}).get('label', '')
            full_review = f"{title}\n{content}" if title else content
            
            rating_str = item.get('im:rating', {}).get('label')
            rating = float(rating_str) if rating_str else None
            
            # App store doesn't provide exact timestamp easily via JSON RSS, we'll use current for MVP 
            # if we can't parse it, or we could use app-store-scraper package for better data.
            # Using current time as fallback.
            
            formatted_data.append({
                "review_id": review_id,
                "source_url": f"https://apps.apple.com/{self.country}/app/id{self.app_id}",
                "original_review": full_review,
                "rating": rating,
                "review_date": datetime.utcnow(), 
                "language": "en",
                "country": self.country,
                "app_version": item.get('im:version', {}).get('label'),
                "author_identifier": item.get('author', {}).get('name', {}).get('label')
            })
            
        return formatted_data
