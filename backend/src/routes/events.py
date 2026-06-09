from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from sqlmodel import select, or_, and_, func
from typing import List, Optional
from datetime import datetime

from src.utils.postegre_connexion import get_async_sqldb
from src.models.nosql.events import EventsCatalog
from src.utils.security_jwt import get_current_user
from src.models import Utilisateur, Evenement, Lieu, Categorie, Tag, EvenementTag, RoleEnum, Organisateur
from src.schemas.events import EventCreate, EventDetail, EventSummary, EventUpdate, VenueSummary, OrganizerSummary, PaginatedEventsResponse, PaginationInfo

router = APIRouter(
    prefix="/events",
    tags=["Events"],
)

from sqlalchemy.orm import selectinload

@router.get("/", response_model=PaginatedEventsResponse)
async def list_events(
    category: Optional[str] = None,
    city: Optional[str] = None,
    price_max: Optional[float] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    session: AsyncSession = Depends(get_async_sqldb)
):
    """Liste les événements avec filtres et pagination (PostgreSQL)"""
    # 1. Requête de base avec pré-chargement des relations nécessaires
    statement = select(Evenement).options(
        selectinload(Evenement.lieu),
        selectinload(Evenement.tags),
        selectinload(Evenement.categorie) # Pré-charge la catégorie pour éviter le Lazy Load Error
    ).join(Lieu).join(Categorie)
    
    # 2. Application des filtres
    if category:
        statement = statement.where(Categorie.nom == category)
    if city:
        statement = statement.where(Lieu.ville == city)
    if price_max is not None:
        statement = statement.where(Evenement.prix <= price_max)
        
    # 3. Calcul du total (Requête simplifiée pour éviter le produit cartésien)
    count_stmt = select(func.count(Evenement.id)).select_from(Evenement).join(Lieu).join(Categorie)
    if category: count_stmt = count_stmt.where(Categorie.nom == category)
    if city: count_stmt = count_stmt.where(Lieu.ville == city)
    if price_max is not None: count_stmt = count_stmt.where(Evenement.prix <= price_max)
    
    total_result = await session.execute(count_stmt)
    total = total_result.scalar() or 0

    # 4. Application de la pagination
    offset = (page - 1) * limit
    statement = statement.offset(offset).limit(limit)
    
    result = await session.execute(statement)
    events = result.scalars().all()
    
    # --- FUSION POLYGLOTTE : Récupération des notes moyennes depuis MongoDB ---
    event_ids = [e.id for e in events]
    ratings_map = {}

    if event_ids:
        from src.models.nosql.reviews import Avis
        pipeline = [
            {"$match": {"event_id": {"$in": event_ids}}},
            {"$group": {
                "_id": "$event_id",
                "avg_rating": {"$avg": "$note_globale"}
            }}
        ]
        mongo_res = await Avis.aggregate(pipeline).to_list()
        ratings_map = {item["_id"]: round(item["avg_rating"], 1) for item in mongo_res}
    
    data = [
        EventSummary(
            id=e.id,
            titre=e.titre,
            description=e.description,
            date_debut=e.date_debut,
            prix=e.prix,
            capacite_max=e.capacite_max,
            image_url=e.image_url,
            statut=e.statut,
            venue=VenueSummary(id=e.lieu.id, nom=e.lieu.nom, ville=e.lieu.ville, adresse=e.lieu.adresse),
            categorie_name=e.categorie.nom,
            tags=[t.libelle for t in e.tags],
            average_rating=ratings_map.get(e.id, 0.0) # Injection de la note MongoDB
        ) for e in events
    ]

    total_pages = (total + limit - 1) // limit if total > 0 else 1

    return PaginatedEventsResponse(
        data=data,
        pagination=PaginationInfo(
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages
        )
    )

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=EventDetail)
async def create_event(
    event_data: EventCreate,
    current_user: Utilisateur = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_sqldb)
):
    """Création d'un événement : Transaction SQL + Insertion MongoDB (Beanie)"""
    
    # 1. Vérification des droits (Organisateur)
    if current_user.role != RoleEnum.organisateur:
        raise HTTPException(status_code=403, detail="Only organizers can create events")
    
    # Récupération de l'ID organisateur
    statement = select(Organisateur).where(Organisateur.id_utilisateur == current_user.id)
    res_org = await session.execute(statement)
    organisateur = res_org.scalar_one_or_none()
    
    if not organisateur:
        raise HTTPException(status_code=400, detail="User is registered as organizer but profile is missing")

    # 2. Insertion SQL - CONVERSION DES DATETIMES AWARE EN NAIVE
    # Les datetimes provenant du frontend via JSON (ISO format avec Z) sont AWARE (timezone-aware)
    # PostgreSQL TIMESTAMP WITHOUT TIME ZONE n'accepte que des NAIVE datetimes (sans timezone)
    date_debut = event_data.date_debut.replace(tzinfo=None) if event_data.date_debut.tzinfo else event_data.date_debut
    date_fin = event_data.date_fin.replace(tzinfo=None) if event_data.date_fin.tzinfo else event_data.date_fin
    
    new_event = Evenement(
        titre=event_data.titre,
        description=event_data.description,
        date_debut=date_debut,
        date_fin=date_fin,
        prix=event_data.prix,
        capacite_max=event_data.capacite_max,
        image_url=event_data.image_url,
        id_lieu=event_data.id_lieu,
        id_categorie=event_data.id_categorie,
        id_organisateur=organisateur.id
    )
    
    try:
        session.add(new_event)
        await session.flush() # Pour récupérer l'ID sans commit définitif
        
        # Gestion des tags (SQL)
        for tag_name in event_data.tags:
            # Récupérer ou créer le tag
            stmt_tag = select(Tag).where(Tag.libelle == tag_name)
            res_tag = await session.execute(stmt_tag)
            tag = res_tag.scalar_one_or_none()
            if not tag:
                tag = Tag(libelle=tag_name)
                session.add(tag)
                await session.flush()
            
            # Liaison
            link = EvenementTag(id_evenement=new_event.id, id_tag=tag.id)
            session.add(link)

        # 3. Insertion MongoDB (Beanie)
        mongo_doc = EventsCatalog(
            event_id=new_event.id,
            type=(await session.get(Categorie, event_data.id_categorie)).nom,
            location=event_data.location.model_dump(),
            metadata=event_data.metadata,
            search_text=f"{new_event.titre} {new_event.description}",
            view_count=0
        )
        await mongo_doc.insert()
        
        # 4. Validation finale
        await session.commit()
        await session.refresh(new_event)
        
        return await get_event_by_id(new_event.id, session)

    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create event: {str(e)}")

@router.get("/nearby", response_model=List[EventSummary])
async def search_nearby(
    lat: float,
    lng: float,
    radius: int = 10000, # mètres
    session: AsyncSession = Depends(get_async_sqldb)
):
    """Recherche géospatiale via Beanie"""
    # 1. MongoDB : Trouver les IDs dans le périmètre
    cursor = await EventsCatalog.find({
        "location": {
            "$near": {
                "$geometry": {"type": "Point", "coordinates": [lng, lat]},
                "$maxDistance": radius
            }
        }
    }).to_list()
    
    event_ids = [doc.event_id for doc in cursor]
    
    if not event_ids:
        return []
        
    # 2. SQL : Récupérer les détails structurels
    stmt = select(Evenement).options(
        selectinload(Evenement.lieu),
        selectinload(Evenement.tags),
        selectinload(Evenement.categorie)
    ).where(Evenement.id.in_(event_ids))
    
    result = await session.execute(stmt)
    events = result.scalars().all()
    
    # Tri par distance (préservé par MongoDB)
    id_map = {e.id: e for e in events}
    sorted_events = [id_map[eid] for eid in event_ids if eid in id_map]
    
    # --- FUSION POLYGLOTTE : Notes ---
    from src.models.nosql.reviews import Avis
    pipeline = [{"$match": {"event_id": {"$in": event_ids}}}, {"$group": {"_id": "$event_id", "avg_rating": {"$avg": "$note_globale"}}}]
    mongo_res = await Avis.aggregate(pipeline).to_list()
    ratings_map = {item["_id"]: round(item["avg_rating"], 1) for item in mongo_res}

    return [
        EventSummary(
            id=e.id,
            titre=e.titre,
            description=e.description,
            date_debut=e.date_debut,
            prix=e.prix,
            capacite_max=e.capacite_max,
            image_url=e.image_url,
            statut=e.statut,
            venue=VenueSummary(id=e.lieu.id, nom=e.lieu.nom, ville=e.lieu.ville, adresse=e.lieu.adresse),
            categorie_name=e.categorie.nom,
            tags=[t.libelle for t in e.tags],
            average_rating=ratings_map.get(e.id, 0.0)
        ) for e in sorted_events
    ]

@router.get("/search", response_model=List[EventSummary])
async def search_events(
    q: str = Query(..., min_length=3),
    session: AsyncSession = Depends(get_async_sqldb)
):
    """Recherche plein-texte via Beanie"""
    # 1. MongoDB : Recherche textuelle
    cursor = await EventsCatalog.find(
        {"$text": {"$search": q}}
    ).sort([("score", {"$meta": "textScore"})]).to_list()
    
    event_ids = [doc.event_id for doc in cursor]
    
    if not event_ids:
        return []
        
    # 2. SQL : Récupérer les détails
    stmt = select(Evenement).options(
        selectinload(Evenement.lieu),
        selectinload(Evenement.tags),
        selectinload(Evenement.categorie)
    ).where(Evenement.id.in_(event_ids))
    
    result = await session.execute(stmt)
    events = result.scalars().all()
    
    # Préserver l'ordre de pertinence
    id_map = {e.id: e for e in events}
    
    # --- FUSION POLYGLOTTE : Notes ---
    from src.models.nosql.reviews import Avis
    pipeline = [{"$match": {"event_id": {"$in": event_ids}}}, {"$group": {"_id": "$event_id", "avg_rating": {"$avg": "$note_globale"}}}]
    mongo_res = await Avis.aggregate(pipeline).to_list()
    ratings_map = {item["_id"]: round(item["avg_rating"], 1) for item in mongo_res}

    return [
        EventSummary(
            id=id_map[eid].id,
            titre=id_map[eid].titre,
            description=id_map[eid].description,
            date_debut=id_map[eid].date_debut,
            prix=id_map[eid].prix,
            capacite_max=id_map[eid].capacite_max,
            image_url=id_map[eid].image_url,
            statut=id_map[eid].statut,
            venue=VenueSummary(id=id_map[eid].lieu.id, nom=id_map[eid].lieu.nom, ville=id_map[eid].lieu.ville, adresse=id_map[eid].lieu.adresse),
            categorie_name=id_map[eid].categorie.nom,
            tags=[t.libelle for t in id_map[eid].tags],
            average_rating=ratings_map.get(eid, 0.0)
        ) for eid in event_ids if eid in id_map
    ]

@router.get("/{event_id}", response_model=EventDetail)
async def get_event_by_id(event_id: int, session: AsyncSession = Depends(get_async_sqldb)):
    """Récupère un événement en agrégeant SQL (structure) et MongoDB (métadonnées)"""
    
    # 1. SQL avec chargement immédiat des relations
    stmt = select(Evenement).options(
        selectinload(Evenement.lieu),
        selectinload(Evenement.organisateur),
        selectinload(Evenement.categorie),
        selectinload(Evenement.tags)
    ).where(Evenement.id == event_id)
    
    res = await session.execute(stmt)
    event = res.scalar_one_or_none()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
        
    # 2. MongoDB (Beanie)
    mongo_data = await EventsCatalog.find_one(EventsCatalog.event_id == event_id)
    
    return EventDetail(
        id=event.id,
        titre=event.titre,
        description=event.description,
        date_debut=event.date_debut,
        date_fin=event.date_fin,
        prix=event.prix,
        capacite_max=event.capacite_max,
        image_url=event.image_url,
        statut=event.statut,
        venue=VenueSummary(id=event.lieu.id, nom=event.lieu.nom, ville=event.lieu.ville, adresse=event.lieu.adresse),
        organizer=OrganizerSummary(id=event.organisateur.id, nom=event.organisateur.nom, est_verifie=event.organisateur.est_verifie),
        categorie_name=event.categorie.nom,
        metadata=mongo_data.metadata if mongo_data else {},
        location=mongo_data.location if mongo_data else {"type": "Point", "coordinates": [0, 0]},
        tags=[t.libelle for t in event.tags]
    )

@router.patch("/{event_id}", response_model=EventDetail)
async def update_event(
    event_id: int,
    update_data: EventUpdate,
    current_user: Utilisateur = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_sqldb)
):
    """Mise à jour d'un événement (SQL + MongoDB)"""
    
    # 1. Vérification de l'existence et des droits
    stmt = select(Evenement).where(Evenement.id == event_id)
    res = await session.execute(stmt)
    event = res.scalar_one_or_none()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Seul l'organisateur de cet event (ou un admin) peut modifier
    statement = select(Organisateur).where(Organisateur.id_utilisateur == current_user.id)
    res_org = await session.execute(statement)
    organisateur = res_org.scalar_one_or_none()
    
    if not organisateur or event.id_organisateur != organisateur.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this event")

    # 2. Mise à jour SQL - Conversion des datetimes AWARE en NAIVE
    update_dict = update_data.model_dump(exclude_unset=True, exclude={"metadata"})
    for key, value in update_dict.items():
        if key in ['date_debut', 'date_fin'] and value is not None and hasattr(value, 'tzinfo') and value.tzinfo:
            value = value.replace(tzinfo=None)
        setattr(event, key, value)
    
    # 3. Mise à jour MongoDB (Beanie)
    if update_data.metadata is not None:
        await EventsCatalog.find_one(EventsCatalog.event_id == event_id).update(
            {"$set": {"metadata": update_data.metadata}}
        )

    await session.commit()
    await session.refresh(event)
    return await get_event_by_id(event.id, session)

@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: int,
    current_user: Utilisateur = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_sqldb)
):
    """Suppression/Annulation d'un événement (Cascade SQL + MongoDB)"""
    
    # 1. Vérification
    stmt = select(Evenement).where(Evenement.id == event_id)
    res = await session.execute(stmt)
    event = res.scalar_one_or_none()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
        
    statement = select(Organisateur).where(Organisateur.id_utilisateur == current_user.id)
    res_org = await session.execute(statement)
    organisateur = res_org.scalar_one_or_none()
    
    if not organisateur or event.id_organisateur != organisateur.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this event")

    # 2. SQL : Annulation via procédure
    await session.execute(text("CALL proc_annuler_evenement(:id)"), {"id": event_id})
    
    # 3. MongoDB (Beanie)
    await EventsCatalog.find_one(EventsCatalog.event_id == event_id).delete()

    await session.commit()
    return None
