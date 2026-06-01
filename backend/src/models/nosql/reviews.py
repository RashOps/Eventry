from beanie import Document, Indexed
from pydantic import Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from pymongo import IndexModel, DESCENDING

class ReviewDetailNoSQL(Document):
    ambiance: int
    organisation: int
    rapport_qualite_prix: int

class OrganizerReplyNoSQL(Document):
    contenu: str
    published_at: datetime = Field(default_factory=datetime.now)

class Avis(Document):
    event_id: Indexed(int)
    user_id: int
    pseudo_utilisateur: str
    avatar_url: Optional[str] = None
    note_globale: int
    notes_detail: Dict[str, int] # ou ReviewDetailNoSQL si on veut imbriquer proprement
    contenu: str
    likes: int = 0
    likes_user_ids: List[int] = []
    published_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    reponse_organisateur: Optional[Dict[str, Any]] = None

    class Settings:
        name = "avis"
        indexes = [
            # Un utilisateur ne peut avoir qu'un seul avis par événement
            IndexModel([("event_id", 1), ("user_id", 1)], unique=True),
            # Récupérer les avis d'un event triés par date
            IndexModel([("event_id", 1), ("published_at", DESCENDING)]),
            # TTL Index (3 ans)
            IndexModel([("published_at", 1)], expireAfterSeconds=94608000)
        ]
