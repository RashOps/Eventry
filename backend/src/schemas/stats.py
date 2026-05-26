from pydantic import BaseModel, Field
from typing import Dict, List, Optional

class ReviewCriteriaStats(BaseModel):
    ambiance: float = 0.0
    organisation: float = 0.0
    rapport_qualite_prix: float = 0.0

class ReviewStats(BaseModel):
    total: int = 0
    average: float = 0.0
    distribution: Dict[str, int] = Field(
        default={"1": 0, "2": 0, "3": 0, "4": 0, "5": 0},
        description="Répartition des notes de 1 à 5"
    )
    average_by_criteria: ReviewCriteriaStats

class EventStatsResponse(BaseModel):
    event_id: int
    title: str
    capacity: int
    registered_count: int
    fill_rate: float
    reviews: ReviewStats

class OrganizerDashboardItem(BaseModel):
    organisateur: str
    evenement: str
    capacite_max: int
    places_occupees: int
    taux_remplissage: float
    ville: str
    categorie: str

class OrganizerDashboardResponse(BaseModel):
    data: List[OrganizerDashboardItem]
    total_events: int
    overall_fill_rate: float
