from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
from src.models.base import StatutInscriptionEnum

class InscriptionBase(SQLModel):
    id_utilisateur: int = Field(foreign_key="utilisateurs.id")
    id_evenement: int = Field(foreign_key="evenements.id")
    statut: StatutInscriptionEnum = Field(default=StatutInscriptionEnum.confirmee)
    places_reservees: int = Field(default=1)

class Inscription(InscriptionBase, table=True):
    __tablename__ = "inscriptions"
    id: Optional[int] = Field(default=None, primary_key=True)
    date_inscription: datetime = Field(default_factory=datetime.now)
    
    # Relations
    utilisateur: "Utilisateur" = Relationship(back_populates="inscriptions")
    evenement: "Evenement" = Relationship(back_populates="inscriptions")
