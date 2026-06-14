from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from sqlalchemy.orm import selectinload
from sqlmodel import select
from typing import List

from src.utils.postegre_connexion import get_async_sqldb
from src.utils.security_jwt import get_current_user
from src.models import Utilisateur, Inscription, Evenement, Lieu
from src.schemas.registrations import (
    RegistrationCreate, 
    RegistrationOut, 
    UserRegistrationsResponse, 
    UserRegistrationItem
)
from src.schemas.events import EventSummary, VenueSummary

router = APIRouter(
    tags=["Registrations"],
)

@router.post("/events/{event_id}/register", status_code=status.HTTP_201_CREATED, response_model=RegistrationOut)
async def register_to_event(
    event_id: int,
    reg_data: RegistrationCreate,
    current_user: Utilisateur = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_sqldb)
):
    """
    Inscrit l'utilisateur à un événement en utilisant la procédure stockée SQL.
    Gère automatiquement la liste d'attente.
    """
    # 1. Vérifier si l'événement existe
    event = await session.get(Evenement, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # 2. Vérifier si déjà inscrit
    stmt = select(Inscription).where(
        Inscription.id_utilisateur == current_user.id,
        Inscription.id_evenement == event_id
    )
    res = await session.execute(stmt)
    existing = res.scalar_one_or_none()
    if existing:
        if existing.statut != "annulee":
            raise HTTPException(status_code=409, detail="Already registered to this event")
        else:
            await session.delete(existing)
            await session.commit()

    # 3. Appel à la procédure stockée (Logique métier SQL)
    # On passe NULL pour le paramètre OUT r_statut
    try:
        await session.execute(
            text("CALL proc_inscrire_participant(:u_id, :e_id, :places, NULL)"),
            {
                "u_id": current_user.id,
                "e_id": event_id,
                "places": reg_data.places_reservees
            }
        )
        await session.commit()
        
        # 4. Récupérer l'inscription créée pour le retour
        stmt_new = select(Inscription).where(
            Inscription.id_utilisateur == current_user.id,
            Inscription.id_evenement == event_id
        )
        res = await session.execute(stmt_new)
        new_registration = res.scalar_one()
        
        return new_registration

    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.delete("/events/{event_id}/register", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_registration(
    event_id: int,
    current_user: Utilisateur = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_sqldb)
):
    """
    Annule une inscription. 
    Le trigger SQL 'tr_after_annulation_inscription' gérera la promotion automatique.
    """
    stmt = select(Inscription).where(
        Inscription.id_utilisateur == current_user.id,
        Inscription.id_evenement == event_id
    )
    res = await session.execute(stmt)
    registration = res.scalar_one_or_none()

    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")

    if registration.statut == "annulee":
        raise HTTPException(status_code=400, detail="Registration already cancelled")

    # Mise à jour du statut -> Déclenche le trigger de promotion
    registration.statut = "annulee"
    session.add(registration)
    await session.commit()
    
    return None

@router.get("/users/{user_id}/registrations", response_model=UserRegistrationsResponse)
async def get_user_registrations(
    user_id: int,
    current_user: Utilisateur = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_sqldb)
):
    """
    Récupère toutes les inscriptions d'un utilisateur avec les détails des événements.
    """
    # Sécurité : Seul le propriétaire peut voir ses inscriptions
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view these registrations")

    stmt = select(Inscription).options(
        selectinload(Inscription.evenement).selectinload(Evenement.lieu),
        selectinload(Inscription.evenement).selectinload(Evenement.tags),
        selectinload(Inscription.evenement).selectinload(Evenement.categorie) # Ajouté pour categorie_name
    ).where(
        Inscription.id_utilisateur == user_id
    ).order_by(Inscription.date_inscription.desc())

    res = await session.execute(stmt)
    inscriptions = res.scalars().all()

    # --- FUSION POLYGLOTTE : Notes ---
    event_ids = list(set([i.id_evenement for i in inscriptions]))
    ratings_map = {}
    if event_ids:
        from src.models.nosql.reviews import Avis
        pipeline = [{"$match": {"event_id": {"$in": event_ids}}}, {"$group": {"_id": "$event_id", "avg_rating": {"$avg": "$note_globale"}}}]
        mongo_res = await Avis.aggregate(pipeline).to_list()
        ratings_map = {item["_id"]: round(item["avg_rating"], 1) for item in mongo_res}

    items = [
        UserRegistrationItem(
            registration_id=i.id,
            status=i.statut,
            places=i.places_reservees,
            registered_at=i.date_inscription,
            event=EventSummary(
                id=i.evenement.id,
                titre=i.evenement.titre,
                description=i.evenement.description, # Ajouté
                date_debut=i.evenement.date_debut,
                prix=i.evenement.prix,
                capacite_max=i.evenement.capacite_max,
                image_url=i.evenement.image_url,
                statut=i.evenement.statut,
                venue=VenueSummary(
                    id=i.evenement.lieu.id,
                    nom=i.evenement.lieu.nom,
                    ville=i.evenement.lieu.ville,
                    adresse=i.evenement.lieu.adresse
                ),
                categorie_name=i.evenement.categorie.nom, # Ajouté
                tags=[t.libelle for t in i.evenement.tags],
                average_rating=ratings_map.get(i.id_evenement, 0.0) # Ajouté
            )
        ) for i in inscriptions
    ]

    return UserRegistrationsResponse(data=items, total=len(items))
