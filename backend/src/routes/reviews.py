from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from datetime import datetime
from typing import List
from bson import ObjectId

from src.utils.postegre_connexion import get_async_sqldb
from src.utils.security_jwt import get_current_user
from src.models import Utilisateur, Evenement, Inscription, Organisateur, StatutInscriptionEnum
from src.models.nosql.reviews import Avis
from src.schemas.reviews import (
    ReviewCreate, 
    ReviewOut, 
    ReviewUpdate, 
    OrganizerReplyRequest,
    UserReviewSummary
)

router = APIRouter(
    tags=["Reviews & Social"],
)

@router.get("/events/{event_id}/reviews", response_model=List[ReviewOut])
async def get_event_reviews(event_id: int):
    """
    Récupère tous les avis d'un événement (Beanie).
    """
    cursor = await Avis.find(Avis.event_id == event_id).sort("-published_at").to_list()
    
    reviews = []
    for doc in cursor:
        review_dict = doc.model_dump()
        review_dict["id"] = str(doc.id)
        # Mapper les champs dénormalisés vers le schéma UserReviewSummary
        review_dict["user"] = {
            "id": doc.user_id,
            "pseudo": doc.pseudo_utilisateur,
            "avatar_url": doc.avatar_url
        }
        reviews.append(ReviewOut(**review_dict))
    
    return reviews

@router.post("/events/{event_id}/reviews", status_code=status.HTTP_201_CREATED, response_model=ReviewOut)
async def create_review(
    event_id: int,
    review_data: ReviewCreate,
    current_user: Utilisateur = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_sqldb)
):
    """
    Dépose un avis sur un événement.
    Vérifie l'inscription confirmée et la fin de l'événement en SQL.
    """
    # 1. Vérifier si l'événement existe
    event = await session.get(Evenement, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # 2. Vérifier si l'événement est fini
    if event.date_fin > datetime.now():
        raise HTTPException(
            status_code=403, 
            detail="You cannot review an event that has not ended yet"
        )

    # 3. Vérifier si l'utilisateur a une inscription confirmée
    stmt = select(Inscription).where(
        Inscription.id_utilisateur == current_user.id,
        Inscription.id_evenement == event_id,
        Inscription.statut == StatutInscriptionEnum.confirmee
    )
    res = await session.execute(stmt)
    if not res.first():
        raise HTTPException(
            status_code=403, 
            detail="You must have a confirmed registration to leave a review"
        )

    # 4. Insertion Beanie
    # Vérifier l'unicité via Beanie
    existing = await Avis.find_one(Avis.event_id == event_id, Avis.user_id == current_user.id)
    if existing:
        raise HTTPException(status_code=409, detail="You have already reviewed this event")

    new_review = Avis(
        event_id=event_id,
        user_id=current_user.id,
        pseudo_utilisateur=current_user.pseudo,
        avatar_url=current_user.avatar_url,
        note_globale=review_data.note_globale,
        notes_detail=review_data.notes_detail.model_dump(),
        contenu=review_data.contenu,
        likes=0,
        likes_user_ids=[],
        published_at=datetime.now()
    )
    
    await new_review.insert()
    
    review_dict = new_review.model_dump()
    review_dict["id"] = str(new_review.id)
    review_dict["user"] = {"id": current_user.id, "pseudo": current_user.pseudo, "avatar_url": current_user.avatar_url}
    
    return ReviewOut(**review_dict)

@router.patch("/reviews/{review_id}", response_model=ReviewOut)
async def update_review(
    review_id: str,
    review_data: ReviewUpdate,
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    Modifie son propre avis (Beanie).
    """
    try:
        oid = ObjectId(review_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid review ID")

    review = await Avis.get(oid)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if review.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this review")

    update_dict = review_data.model_dump(exclude_unset=True)
    if "notes_detail" in update_dict:
        update_dict["notes_detail"] = review_data.notes_detail.model_dump()
    
    update_dict["updated_at"] = datetime.now()

    await review.update({"$set": update_dict})
    
    # Rafraîchir pour le retour
    updated_review = await Avis.get(oid)
    review_dict = updated_review.model_dump()
    review_dict["id"] = str(updated_review.id)
    review_dict["user"] = {"id": current_user.id, "pseudo": current_user.pseudo, "avatar_url": current_user.avatar_url}
    
    return ReviewOut(**review_dict)

@router.delete("/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: str,
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    Supprime son propre avis (Beanie).
    """
    try:
        oid = ObjectId(review_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid review ID")

    review = await Avis.get(oid)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if review.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this review")

    await review.delete()
    return None

@router.post("/reviews/{review_id}/reply", status_code=status.HTTP_201_CREATED, response_model=ReviewOut)
async def reply_to_review(
    review_id: str,
    reply_data: OrganizerReplyRequest,
    current_user: Utilisateur = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_sqldb)
):
    """
    Permet à l'organisateur de l'événement de répondre à un avis (Beanie).
    """
    try:
        oid = ObjectId(review_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid review ID")

    review = await Avis.get(oid)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    # Vérifier si current_user est l'organisateur de l'événement lié à l'avis
    event_id = review.event_id
    stmt = select(Evenement).where(Evenement.id == event_id)
    res = await session.execute(stmt)
    event = res.scalar_one_or_none()

    stmt_org = select(Organisateur).where(Organisateur.id_utilisateur == current_user.id)
    res_org = await session.execute(stmt_org)
    organisateur = res_org.scalar_one_or_none()

    if not organisateur or event.id_organisateur != organisateur.id:
        raise HTTPException(
            status_code=403, 
            detail="Only the organizer of this event can reply to reviews"
        )

    # Mise à jour Beanie
    reply_doc = {
        "contenu": reply_data.contenu,
        "published_at": datetime.now()
    }
    
    await review.update({"$set": {"reponse_organisateur": reply_doc}})

    updated_review = await Avis.get(oid)
    review_dict = updated_review.model_dump()
    review_dict["id"] = str(updated_review.id)
    review_dict["user"] = {
        "id": updated_review.user_id,
        "pseudo": updated_review.pseudo_utilisateur,
        "avatar_url": updated_review.avatar_url
    }
    
    return ReviewOut(**review_dict)
