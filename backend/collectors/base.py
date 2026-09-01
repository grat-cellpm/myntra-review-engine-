from abc import ABC, abstractmethod
from typing import List
import datetime
from database.models import RawReview

class BaseCollector(ABC):
    """Base interface for all data collectors."""
    
    @abstractmethod
    def fetch_reviews(self, limit: int = 100) -> List[dict]:
        """Fetch raw reviews from the source."""
        pass
    
    def process_to_models(self, raw_data: List[dict]) -> List[RawReview]:
        """Convert raw dict data to SQLAlchemy models."""
        models = []
        for item in raw_data:
            model = RawReview(
                review_id=str(item.get("review_id")),
                source=self.source_name,
                source_url=item.get("source_url"),
                original_review=item.get("original_review"),
                rating=item.get("rating"),
                review_date=item.get("review_date"),
                collected_at=datetime.datetime.utcnow(),
                language=item.get("language"),
                country=item.get("country"),
                app_version=item.get("app_version"),
                author_identifier=item.get("author_identifier")
            )
            models.append(model)
        return models

    @property
    @abstractmethod
    def source_name(self) -> str:
        pass
