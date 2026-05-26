import pytest
import time
from httpx import AsyncClient
from datetime import datetime, timedelta
from sqlalchemy import text
from src.models import Evenement, Inscription, StatutInscriptionEnum, StatutEventEnum

async def create_test_user(client: AsyncClient, pseudo: str):
    """Utilitaire pour créer un utilisateur unique"""
    email = f"{pseudo.lower()}@test.com"
    payload = {"email": email, "pseudo": pseudo, "password": "password123"}
    await client.post("/api/v1/auth/register", json=payload)
    login_res = await client.post("/api/v1/auth/login", data={"username": email, "password": "password123"})
    return login_res.json()["access_token"]

@pytest.mark.asyncio
async def test_create_review_flow(client: AsyncClient, session):
    """
    Scénario complet : 
    1. Un événement passé est créé.
    2. Un utilisateur s'y inscrit (Confirmé).
    3. L'utilisateur dépose un avis.
    4. L'organisateur répond.
    """
    
    # --- 1. SETUP EVENT PASSÉ ---
    stmt = text("""
        INSERT INTO evenements (titre, description, date_debut, date_fin, prix, capacite_max, id_lieu, id_organisateur, id_categorie, statut)
        VALUES ('Event Fini', 'Desc', NOW() - INTERVAL '5 days', NOW() - INTERVAL '1 day', 0, 100, 1, 1, 1, 'published')
        RETURNING id
    """)
    res = await session.execute(stmt)
    event_id = res.scalar()
    await session.commit()

    # --- 2. SETUP USER & INSCRIPTION ---
    token_user = await create_test_user(client, f"Reviewer_{int(time.time()*1000)}")
    headers_user = {"Authorization": f"Bearer {token_user}"}
    
    # Inscription
    await client.post(f"/api/v1/events/{event_id}/register", json={"places_reservees": 1}, headers=headers_user)

    # --- 3. DÉPÔT D'AVIS (POST) ---
    review_payload = {
        "note_globale": 5,
        "notes_detail": {"ambiance": 5, "organisation": 4, "rapport_qualite_prix": 5},
        "contenu": "C'était vraiment incroyable !"
    }
    response = await client.post(f"/api/v1/events/{event_id}/reviews", json=review_payload, headers=headers_user)
    
    assert response.status_code == 201
    review_data = response.json()
    # On vérifie que '_id' est présent (format MongoDB brut retourné par FastAPI)
    assert "_id" in review_data
    review_id = review_data["_id"]

    # --- 4. RÉPONSE ORGANISATEUR ---
    login_admin = {"username": "admin@eventry.fr", "password": "password123"}
    res_a = await client.post("/api/v1/auth/login", data=login_admin)
    token_admin = res_a.json()["access_token"]
    
    reply_payload = {"contenu": "Merci beaucoup pour ce retour !"}
    # Utilisation de la route correcte enregistrée dans main.py
    res_reply = await client.post(f"/api/v1/reviews/{review_id}/reply", json=reply_payload, headers={"Authorization": f"Bearer {token_admin}"})
    
    assert res_reply.status_code == 201
    assert res_reply.json()["reponse_organisateur"]["contenu"] == reply_payload["contenu"]

@pytest.mark.asyncio
async def test_review_unauthorized_event_not_ended(client: AsyncClient, session):
    """Vérifie qu'on ne peut pas noter un événement qui n'est pas fini"""
    token = await create_test_user(client, f"BadReviewer_{int(time.time()*1001)}")
    
    # Event 2 (Expo Basquiat) finit en Juin 2026 (dans le futur)
    payload = {
        "note_globale": 5,
        "notes_detail": {"ambiance": 5, "organisation": 5, "rapport_qualite_prix": 5},
        "contenu": "Trop hâte !"
    }
    response = await client.post(f"/api/v1/events/2/reviews", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    assert "not ended" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_review_unauthorized_no_registration(client: AsyncClient, session):
    """Vérifie qu'on ne peut pas noter sans inscription confirmée"""
    # On crée un event fini pour ne pas être bloqué par la date
    stmt = text("""
        INSERT INTO evenements (titre, description, date_debut, date_fin, prix, capacite_max, id_lieu, id_organisateur, id_categorie, statut)
        VALUES ('Event Fini Sans Inscr', 'Desc', NOW() - INTERVAL '5 days', NOW() - INTERVAL '1 day', 0, 100, 1, 1, 1, 'published')
        RETURNING id
    """)
    res = await session.execute(stmt)
    event_id = res.scalar()
    await session.commit()

    token = await create_test_user(client, f"Stranger_{int(time.time()*1002)}")
    
    payload = {
        "note_globale": 1,
        "notes_detail": {"ambiance": 1, "organisation": 1, "rapport_qualite_prix": 1},
        "contenu": "Je n'y suis pas allé mais je note quand même"
    }
    response = await client.post(f"/api/v1/events/{event_id}/reviews", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    assert "confirmed registration" in response.json()["detail"].lower()

@pytest.mark.asyncio
async def test_get_reviews(client: AsyncClient):
    """Vérifie la lecture des avis d'un événement"""
    # Event 1 a déjà des avis dans le seed Mongo
    response = await client.get("/api/v1/events/1/reviews")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    assert "user" in data[0]
    assert "pseudo" in data[0]["user"]
