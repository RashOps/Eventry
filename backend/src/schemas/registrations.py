from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
from src.models.base import StatutInscriptionEnum
from src.schemas.events import EventSummary

class RegistrationBase(BaseModel):
    places_reservees: int = Field(default=1, gt=0, description="Nombre de places à réserver")

class RegistrationCreate(RegistrationBase):
    pass

class RegistrationOut(BaseModel):
    id: int
    id_utilisateur: int
    id_evenement: int
    statut: StatutInscriptionEnum
    places_reservees: int
    date_inscription: datetime

    class Config:
        from_attributes = True

class UserRegistrationItem(BaseModel):
    registration_id: int
    status: StatutInscriptionEnum
    places: int
    registered_at: datetime
    event: EventSummary

class UserRegistrationsResponse(BaseModel):
    data: List[UserRegistrationItem]
    total: int
