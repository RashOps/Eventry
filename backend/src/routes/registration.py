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
    existing = await session.execute(stmt)
    if existing.first():
        raise HTTPException(status_code=409, detail="Already registered to this event")

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
        selectinload(Inscription.evenement).selectinload(Evenement.tags)
    ).where(
        Inscription.id_utilisateur == user_id
    ).order_by(Inscription.date_inscription.desc())

    res = await session.execute(stmt)
    inscriptions = res.scalars().all()

    items = [
        UserRegistrationItem(
            registration_id=i.id,
            status=i.statut,
            places=i.places_reservees,
            registered_at=i.date_inscription,
            event=EventSummary(
                id=i.evenement.id,
                titre=i.evenement.titre,
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
                tags=[t.libelle for t in i.evenement.tags]
            )
        ) for i in inscriptions
    ]

    return UserRegistrationsResponse(data=items, total=len(items))
