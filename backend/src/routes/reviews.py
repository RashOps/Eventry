from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from datetime import datetime
from typing import List
from bson import ObjectId

from src.utils.postegre_connexion import get_async_sqldb
from src.utils.mongo_connexion import get_db_nosql
from src.utils.security_jwt import get_current_user
from src.models import Utilisateur, Evenement, Inscription, Organisateur, StatutInscriptionEnum
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
    Récupère tous les avis d'un événement (MongoDB).
    """
    db_nosql = get_db_nosql()
    cursor = db_nosql.avis.find({"event_id": event_id}).sort("published_at", -1)
    
    reviews = []
    for doc in cursor:
        doc["id"] = str(doc["_id"])
        doc["_id"] = str(doc["_id"])
        # Mapper les champs dénormalisés vers le schéma UserReviewSummary
        doc["user"] = {
            "id": doc["user_id"],
            "pseudo": doc.get("pseudo_utilisateur", "Anonyme"),
            "avatar_url": doc.get("avatar_url")
        }
        reviews.append(doc)
    
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

    # 4. Insertion MongoDB
    db_nosql = get_db_nosql()
    
    # Vérifier l'unicité (Index Mongo gère normalement, mais on fait un check API propre)
    existing = db_nosql.avis.find_one({"event_id": event_id, "user_id": current_user.id})
    if existing:
        raise HTTPException(status_code=409, detail="You have already reviewed this event")

    mongo_doc = {
        "event_id": event_id,
        "user_id": current_user.id,
        "pseudo_utilisateur": current_user.pseudo,
        "avatar_url": current_user.avatar_url,
        "note_globale": review_data.note_globale,
        "notes_detail": review_data.notes_detail.model_dump(),
        "contenu": review_data.contenu,
        "likes": 0,
        "likes_user_ids": [],
        "published_at": datetime.now(),
        "reponse_organisateur": None
    }
    
    result = db_nosql.avis.insert_one(mongo_doc)
    
    # Pour le retour, on récupère le document propre
    created_review = db_nosql.avis.find_one({"_id": result.inserted_id})
    created_review["_id"] = str(created_review["_id"])
    created_review["user"] = {"id": current_user.id, "pseudo": current_user.pseudo, "avatar_url": current_user.avatar_url}
    
    # On valide et on retourne via le schéma pour forcer la structure correcte (id aliasé)
    return ReviewOut(**created_review)

@router.patch("/reviews/{review_id}", response_model=ReviewOut)
async def update_review(
    review_id: str,
    review_data: ReviewUpdate,
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    Modifie son propre avis.
    """
    db_nosql = get_db_nosql()
    try:
        oid = ObjectId(review_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid review ID")

    review = db_nosql.avis.find_one({"_id": oid})
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if review["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this review")

    update_fields = review_data.model_dump(exclude_unset=True)
    if "notes_detail" in update_fields:
        update_fields["notes_detail"] = review_data.notes_detail.model_dump()
    
    update_fields["updated_at"] = datetime.now()

    db_nosql.avis.update_one({"_id": oid}, {"$set": update_fields})
    
    updated_doc = db_nosql.avis.find_one({"_id": oid})
    updated_doc["_id"] = str(updated_doc["_id"])
    updated_doc["user"] = {"id": current_user.id, "pseudo": current_user.pseudo, "avatar_url": current_user.avatar_url}
    
    return updated_doc

@router.delete("/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: str,
    current_user: Utilisateur = Depends(get_current_user)
):
    """
    Supprime son propre avis.
    """
    db_nosql = get_db_nosql()
    try:
        oid = ObjectId(review_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid review ID")

    review = db_nosql.avis.find_one({"_id": oid})
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if review["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this review")

    db_nosql.avis.delete_one({"_id": oid})
    return None

@router.post("/reviews/{review_id}/reply", status_code=status.HTTP_201_CREATED, response_model=ReviewOut)
async def reply_to_review(
    review_id: str,
    reply_data: OrganizerReplyRequest,
    current_user: Utilisateur = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_sqldb)
):
    """
    Permet à l'organisateur de l'événement de répondre à un avis.
    """
    db_nosql = get_db_nosql()
    try:
        oid = ObjectId(review_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid review ID")

    review = db_nosql.avis.find_one({"_id": oid})
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    # Vérifier si current_user est l'organisateur de l'événement lié à l'avis
    event_id = review["event_id"]
    stmt = select(Evenement).where(Evenement.id == event_id)
    res = await session.execute(stmt)
    event = res.scalar_one_or_none()

    # Récupérer le profil organisateur de l'utilisateur connecté
    stmt_org = select(Organisateur).where(Organisateur.id_utilisateur == current_user.id)
    res_org = await session.execute(stmt_org)
    organisateur = res_org.scalar_one_or_none()

    if not organisateur or event.id_organisateur != organisateur.id:
        raise HTTPException(
            status_code=403, 
            detail="Only the organizer of this event can reply to reviews"
        )

    # Mise à jour MongoDB
    reply_doc = {
        "contenu": reply_data.contenu,
        "published_at": datetime.now()
    }
    
    db_nosql.avis.update_one(
        {"_id": oid},
        {"$set": {"reponse_organisateur": reply_doc}}
    )

    updated_review = db_nosql.avis.find_one({"_id": oid})
    updated_review["_id"] = str(updated_review["_id"])
    # Note: On garde les infos du user qui a posté l'avis pour le retour
    updated_review["user"] = {
        "id": updated_review["user_id"],
        "pseudo": updated_review["pseudo_utilisateur"],
        "avatar_url": updated_review["avatar_url"]
    }
    
    return updated_review
