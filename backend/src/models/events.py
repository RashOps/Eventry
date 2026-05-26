from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from src.models.base import StatutEventEnum

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import ENUM

class EvenementTag(SQLModel, table=True):
    __tablename__ = "evenements_tags"
    id_evenement: int = Field(foreign_key="evenements.id", primary_key=True)
    id_tag: int = Field(foreign_key="tags.id", primary_key=True)

class LieuBase(SQLModel):
    nom: str
    adresse: str
    ville: str
    code_postal: str
    pays: str = Field(default="France")
    latitude: Decimal = Field(max_digits=9, decimal_places=6)
    longitude: Decimal = Field(max_digits=9, decimal_places=6)
    capacite: Optional[int] = None

class Lieu(LieuBase, table=True):
    __tablename__ = "lieux"
    id: Optional[int] = Field(default=None, primary_key=True)
    
    evenements: List["Evenement"] = Relationship(back_populates="lieu")

class CategorieBase(SQLModel):
    nom: str = Field(unique=True)
    description: Optional[str] = None

class Categorie(CategorieBase, table=True):
    __tablename__ = "categories"
    id: Optional[int] = Field(default=None, primary_key=True)
    
    evenements: List["Evenement"] = Relationship(back_populates="categorie")

class TagBase(SQLModel):
    libelle: str = Field(unique=True)

class Tag(TagBase, table=True):
    __tablename__ = "tags"
    id: Optional[int] = Field(default=None, primary_key=True)
    
    evenements: List["Evenement"] = Relationship(back_populates="tags", link_model=EvenementTag)

class EvenementBase(SQLModel):
    titre: str
    description: str
    date_debut: datetime
    date_fin: datetime
    prix: Decimal = Field(default=0.00, max_digits=8, decimal_places=2)
    capacite_max: int
    image_url: Optional[str] = None
    statut: StatutEventEnum = Field(
        sa_column=Column(ENUM(StatutEventEnum, name="statut_event_enum"), default=StatutEventEnum.draft)
    )

class Evenement(EvenementBase, table=True):
    __tablename__ = "evenements"
    id: Optional[int] = Field(default=None, primary_key=True)
    date_creation: datetime = Field(default_factory=datetime.now)
    
    id_lieu: int = Field(foreign_key="lieux.id")
    id_organisateur: int = Field(foreign_key="organisateurs.id")
    id_categorie: int = Field(foreign_key="categories.id")
    
    # Relations
    lieu: Lieu = Relationship(back_populates="evenements")
    organisateur: "Organisateur" = Relationship(back_populates="evenements")
    categorie: Categorie = Relationship(back_populates="evenements")
    tags: List[Tag] = Relationship(back_populates="evenements", link_model=EvenementTag)
    inscriptions: List["Inscription"] = Relationship(back_populates="evenement")
