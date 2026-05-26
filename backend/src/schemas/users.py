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
