from pydantic import BaseModel, Field, field_validator
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
    
    @field_validator('date_debut', 'date_fin', mode='before')
    @classmethod
    def normalize_datetime(cls, v):
        """Convertir les datetimes AWARE (avec timezone) en NAIVE pour PostgreSQL TIMESTAMP WITHOUT TIME ZONE"""
        if isinstance(v, datetime) and v.tzinfo is not None:
            return v.replace(tzinfo=None)
        return v

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
    
    @field_validator('date_debut', 'date_fin', mode='before')
    @classmethod
    def normalize_datetime(cls, v):
        """Convertir les datetimes AWARE en NAIVE pour PostgreSQL"""
        if isinstance(v, datetime) and v.tzinfo is not None:
            return v.replace(tzinfo=None)
        return v

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
    description: str # Ajouté pour l'aperçu sur les cards
    date_debut: datetime
    prix: Decimal
    capacite_max: int
    image_url: Optional[str] = None
    statut: StatutEventEnum
    
    venue: VenueSummary
    categorie_name: str # Ajouté pour le badge sur les cards
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

# --- Modèles de Pagination ---

class PaginationInfo(BaseModel):
    total: int
    page: int
    limit: int
    total_pages: int

class PaginatedEventsResponse(BaseModel):
    data: List[EventSummary]
    pagination: PaginationInfo
