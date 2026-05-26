from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from datetime import datetime
from decimal import Decimal
from src.models.base import StatutEventEnum

# --- Modèles de base pour l'API ---

class LocationSchema(BaseModel):
    type: str = "Point"
    coordinates: List[float] # [lng, lat]

class EventBase(BaseModel):
    titre: str
    description: str
    date_debut: datetime
    date_fin: datetime
    prix: Decimal = Field(default=0.00)
    capacite_max: int
    id_lieu: int
    id_categorie: int
    image_url: Optional[str] = None

class EventCreate(EventBase):
    tags: List[str] = []
    # Données destinées à MongoDB
    metadata: Dict[str, Any] = {}
    location: LocationSchema

class EventUpdate(BaseModel):
    titre: Optional[str] = None
    description: Optional[str] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    prix: Optional[Decimal] = None
    capacite_max: Optional[int] = None
    statut: Optional[StatutEventEnum] = None
    metadata: Optional[Dict[str, Any]] = None

# --- Modèles de réponse (SQL + MongoDB) ---

class VenueSummary(BaseModel):
    id: int
    nom: str
    ville: str
    adresse: str

class OrganizerSummary(BaseModel):
    id: int
    nom: str
    est_verifie: bool

class EventSummary(BaseModel):
    id: int
    titre: str
    date_debut: datetime
    prix: Decimal
    capacite_max: int
    image_url: Optional[str] = None
    statut: StatutEventEnum
    
    venue: VenueSummary
    tags: List[str] = []
    average_rating: float = 0.0

class EventDetail(EventSummary):
    description: str
    date_fin: datetime
    organizer: OrganizerSummary
    categorie_name: str
    
    # Données venant de MongoDB
    metadata: Dict[str, Any] = {}
    location: LocationSchema
    total_reviews: int = 0
