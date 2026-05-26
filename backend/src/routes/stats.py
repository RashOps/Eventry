from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func
from typing import List
from sqlalchemy import text

from src.utils.postegre_connexion import get_async_sqldb
from src.utils.security_jwt import get_current_user
from src.models import Utilisateur, Evenement, Inscription, Organisateur, RoleEnum
from src.models.nosql.reviews import Avis
from src.schemas.stats import (
    EventStatsResponse, 
    ReviewStats, 
    ReviewCriteriaStats,
    OrganizerDashboardResponse,
    OrganizerDashboardItem
)

router = APIRouter(
    tags=["Statistics & Dashboard"],
)

@router.get("/events/{event_id}/stats", response_model=EventStatsResponse)
async def get_event_stats(
    event_id: int,
    current_user: Utilisateur = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_sqldb)
):
    """
    Stats complètes d'un événement (Agrégation SQL + Beanie).
    """
    # 1. Vérification des droits (Organisateur de l'event)
    event = await session.get(Evenement, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Récupérer l'ID organisateur du profil de l'utilisateur connecté
    stmt_org = select(Organisateur).where(Organisateur.id_utilisateur == current_user.id)
    res_org = await session.execute(stmt_org)
    organisateur = res_org.scalar_one_or_none()

    if not organisateur or event.id_organisateur != organisateur.id:
        raise HTTPException(
            status_code=403, 
            detail="Only the organizer of this event can access its statistics"
        )

    # 2. SQL : Calcul du taux de remplissage
    stmt_count = select(func.sum(Inscription.places_reservees)).where(
        Inscription.id_evenement == event_id,
        Inscription.statut == "confirmee"
    )
    res_count = await session.execute(stmt_count)
    registered_count = res_count.scalar() or 0
    
    fill_rate = round((registered_count / event.capacite_max) * 100, 2) if event.capacite_max > 0 else 0

    # 3. MongoDB (Beanie) : Agrégation des avis
    pipeline = [
        {"$match": {"event_id": event_id}},
        {"$group": {
            "_id": "$event_id",
            "total_reviews": {"$sum": 1},
            "avg_rating": {"$avg": "$note_globale"},
            "avg_ambiance": {"$avg": "$notes_detail.ambiance"},
            "avg_organisation": {"$avg": "$notes_detail.organisation"},
            "avg_prix": {"$avg": "$notes_detail.rapport_qualite_prix"},
            "distribution": {"$push": "$note_globale"}
        }}
    ]
    
    mongo_res = await Avis.aggregate(pipeline).to_list()
    
    # Valeurs par défaut si aucun avis
    review_stats = ReviewStats(
        total=0,
        average=0.0,
        distribution={"1": 0, "2": 0, "3": 0, "4": 0, "5": 0},
        average_by_criteria=ReviewCriteriaStats()
    )

    if mongo_res:
        data = mongo_res[0]
        # Calcul de la distribution
        dist = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
        for note in data["distribution"]:
            dist[str(note)] += 1
            
        review_stats = ReviewStats(
            total=data["total_reviews"],
            average=round(data["avg_rating"], 1),
            distribution=dist,
            average_by_criteria=ReviewCriteriaStats(
                ambiance=round(data["avg_ambiance"], 1),
                organisation=round(data["avg_organisation"], 1),
                rapport_qualite_prix=round(data["avg_prix"], 1)
            )
        )

    return EventStatsResponse(
        event_id=event.id,
        title=event.titre,
        capacity=event.capacite_max,
        registered_count=registered_count,
        fill_rate=fill_rate,
        reviews=review_stats
    )

@router.get("/dashboard", response_model=OrganizerDashboardResponse)
async def get_organizer_dashboard(
    current_user: Utilisateur = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_sqldb)
):
    """
    Vue globale de tous ses événements via la vue complexe PostgreSQL.
    """
    if current_user.role != RoleEnum.organisateur:
        raise HTTPException(status_code=403, detail="Only organizers can access the dashboard")

    # Récupérer le nom de l'organisation pour filtrer la vue
    stmt_org = select(Organisateur).where(Organisateur.id_utilisateur == current_user.id)
    res_org = await session.execute(stmt_org)
    organisateur = res_org.scalar_one_or_none()

    if not organisateur:
        raise HTTPException(status_code=400, detail="Organizer profile not found")

    # 2. Requêtage de la vue complexe SQL
    query = text("SELECT * FROM v_dashboard_organisateur WHERE organisateur = :org_name")
    result = await session.execute(query, {"org_name": organisateur.nom})
    rows = result.fetchall()

    dashboard_items = []
    total_fill = 0.0
    for row in rows:
        item = OrganizerDashboardItem(
            organisateur=row.organisateur,
            evenement=row.evenement,
            capacite_max=row.capacite_max,
            places_occupees=row.places_occupees,
            taux_remplissage=float(row.taux_remplissage),
            ville=row.ville,
            categorie=row.categorie
        )
        dashboard_items.append(item)
        total_fill += float(row.taux_remplissage)

    overall_rate = round(total_fill / len(dashboard_items), 2) if dashboard_items else 0.0

    return OrganizerDashboardResponse(
        data=dashboard_items,
        total_events=len(dashboard_items),
        overall_fill_rate=overall_rate
    )
