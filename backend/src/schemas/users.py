from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    VISITEUR = "visiteur"
    PARTICIPANT = "participant"
    ORGANISATEUR = "organisateur"

class UserBase(BaseModel):
    email: EmailStr
    pseudo: str

class UserCreate(UserBase):
    password: str
    role: Optional[UserRole] = UserRole.PARTICIPANT
    # Informations pour le profil organisateur (requis si role == organisateur)
    nom_organisation: Optional[str] = Field(None, min_length=2, max_length=255)
    description_organisation: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    pseudo: Optional[str] = None
    avatar_url: Optional[HttpUrl] = None

class UserOut(UserBase):
    id: int
    role: UserRole
    avatar_url: Optional[str] = None
    date_inscription: datetime
    est_actif: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
