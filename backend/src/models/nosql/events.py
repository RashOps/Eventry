from beanie import Document, Indexed
from pydantic import Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from pymongo import IndexModel, GEOSPHERE, TEXT

class EventsCatalog(Document):
    event_id: Indexed(int, unique=True)
    type: str
    location: Dict[str, Any] # Format GeoJSON {type: "Point", coordinates: [lng, lat]}
    metadata: Dict[str, Any]
    search_text: str
    view_count: int = 0
    created_at: datetime = Field(default_factory=datetime.now)

    class Settings:
        name = "events_catalog"
        indexes = [
            IndexModel([("location", GEOSPHERE)]),
            IndexModel([("search_text", TEXT)])
        ]
