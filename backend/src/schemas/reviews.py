from pydantic import BaseModel, Field, conint, ConfigDict
from datetime import datetime
from typing import Optional, Dict, List

class ReviewDetail(BaseModel):
    ambiance: conint(ge=1, le=5)
    organisation: conint(ge=1, le=5)
    rapport_qualite_prix: conint(ge=1, le=5)

class OrganizerReplyOut(BaseModel):
    contenu: str
    published_at: datetime

class OrganizerReplyRequest(BaseModel):
    contenu: str = Field(..., min_length=1, max_length=1000)

class ReviewCreate(BaseModel):
    note_globale: conint(ge=1, le=5)
    notes_detail: ReviewDetail
    contenu: str = Field(..., min_length=5, max_length=2000)

class ReviewUpdate(BaseModel):
    note_globale: Optional[conint(ge=1, le=5)] = None
    notes_detail: Optional[ReviewDetail] = None
    contenu: Optional[str] = Field(None, min_length=5, max_length=2000)

class UserReviewSummary(BaseModel):
    id: int
    pseudo: str
    avatar_url: Optional[str] = None

class ReviewOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    
    id: str = Field(..., alias="_id")
    event_id: int
    user: UserReviewSummary
    note_globale: int
    notes_detail: ReviewDetail
    contenu: str
    likes: int = 0
    likes_user_ids: List[int] = []
    published_at: datetime
    updated_at: Optional[datetime] = None
    reponse_organisateur: Optional[OrganizerReplyOut] = None
