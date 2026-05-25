from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from src.models.base import RoleEnum

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import ENUM

class UtilisateurBase(SQLModel):
    email: str = Field(unique=True, index=True)
    pseudo: str = Field(unique=True, index=True)
    role: RoleEnum = Field(
        sa_column=Column(ENUM(RoleEnum, name="role_enum"), default=RoleEnum.participant)
    )
    avatar_url: Optional[str] = None
    est_actif: bool = Field(default=True)

class Utilisateur(UtilisateurBase, table=True):
    __tablename__ = "utilisateurs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    mot_de_passe_hash: str
    date_inscription: datetime = Field(default_factory=datetime.now)
    
    # Relations
    organisateur_profil: Optional["Organisateur"] = Relationship(back_populates="utilisateur")
    inscriptions: List["Inscription"] = Relationship(back_populates="utilisateur")

class OrganisateurBase(SQLModel):
    nom: str
    description: Optional[str] = None
    site_web: Optional[str] = None
    est_verifie: bool = Field(default=False)

class Organisateur(OrganisateurBase, table=True):
    __tablename__ = "organisateurs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    id_utilisateur: int = Field(foreign_key="utilisateurs.id", unique=True)
    date_creation: datetime = Field(default_factory=datetime.now)
    
    # Relations
    utilisateur: Utilisateur = Relationship(back_populates="organisateur_profil")
    evenements: List["Evenement"] = Relationship(back_populates="organisateur")
