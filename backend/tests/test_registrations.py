import pytest
import time
from httpx import AsyncClient
from sqlalchemy import text
from src.models.transactions import Inscription
from src.models.users import Utilisateur
from sqlmodel import select

async def create_fresh_user(client: AsyncClient):
    """Utilitaire pour créer un utilisateur unique pour chaque test"""
    ts = int(time.time() * 1000)
    payload = {
        "email": f"user_{ts}@test.com",
        "pseudo": f"User_{ts}",
        "password": "password123"
    }
    await client.post("/api/v1/auth/register", json=payload)
    # Login pour avoir le token
    login_res = await client.post("/api/v1/auth/login", data={"username": payload["email"], "password": payload["password"]})
    return login_res.json()["access_token"], payload

@pytest.mark.asyncio
async def test_register_nominal(client: AsyncClient):
    """Teste une inscription réussie sur un événement avec de la place"""
    token, _ = await create_fresh_user(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Inscription à l'Expo Basquiat (ID 2)
    payload = {"places_reservees": 1}
    response = await client.post("/api/v1/events/2/register", json=payload, headers=headers)
    
    assert response.status_code == 201
    assert response.json()["statut"] == "confirmee"

@pytest.mark.asyncio
async def test_register_waiting_list(client: AsyncClient):
    """Teste le passage automatique en liste d'attente"""
    token, _ = await create_fresh_user(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Event 1 (Nuit Électro) a une capacité de 10. 
    # Seed a déjà 9 confirmés.
    # On prend 2 places -> Doit aller en liste d'attente.
    payload = {"places_reservees": 2}
    response = await client.post("/api/v1/events/1/register", json=payload, headers=headers)
    
    assert response.status_code == 201
    assert response.json()["statut"] == "liste_attente"

@pytest.mark.asyncio
async def test_register_duplicate(client: AsyncClient):
    """Vérifie qu'on ne peut pas s'inscrire deux fois"""
    token, _ = await create_fresh_user(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Première inscription
    await client.post("/api/v1/events/2/register", json={"places_reservees": 1}, headers=headers)
    
    # Deuxième tentative
    response = await client.post("/api/v1/events/2/register", json={"places_reservees": 1}, headers=headers)
    assert response.status_code == 409
    assert "Already registered" in response.json()["detail"]

@pytest.mark.asyncio
async def test_cancel_and_promotion(client: AsyncClient, session):
    """SCÉNARIO CRITIQUE : Annulation et promotion automatique via Trigger SQL"""
    # 1. On crée un événement frais pour éviter les effets de bord du seed
    stmt_event = text("""
        INSERT INTO evenements (titre, description, date_debut, date_fin, prix, capacite_max, id_lieu, id_organisateur, id_categorie, statut)
        VALUES ('Event Promo', 'Test', NOW(), NOW() + INTERVAL '1 day', 10, 1, 1, 1, 1, 'published')
        RETURNING id
    """)
    res_event = await session.execute(stmt_event)
    event_id = res_event.scalar()
    await session.commit()

    # 2. On crée un utilisateur qui va saturer l'event (User A)
    token_a, _ = await create_fresh_user(client)
    # Capacité: 1. User A prend la place.
    res_a = await client.post(f"/api/v1/events/{event_id}/register", json={"places_reservees": 1}, headers={"Authorization": f"Bearer {token_a}"})
    assert res_a.json()["statut"] == "confirmee"

    # 3. On crée un utilisateur qui va aller en liste d'attente (User B)
    token_b, info_b = await create_fresh_user(client)
    res_b = await client.post(f"/api/v1/events/{event_id}/register", json={"places_reservees": 1}, headers={"Authorization": f"Bearer {token_b}"})
    assert res_b.json()["statut"] == "liste_attente"

    # 4. User A annule
    res_cancel = await client.delete(f"/api/v1/events/{event_id}/register", headers={"Authorization": f"Bearer {token_a}"})
    assert res_cancel.status_code == 204

    # 5. VÉRIFICATION DU TRIGGER : User B doit être promu
    stmt_u = select(Utilisateur.id).where(Utilisateur.email == info_b["email"])
    user_b_id = (await session.execute(stmt_u)).scalar_one()
    
    # On récupère l'inscription de B
    stmt_reg = select(Inscription).where(
        Inscription.id_utilisateur == user_b_id,
        Inscription.id_evenement == event_id
    )
    res_reg = await session.execute(stmt_reg)
    reg_b = res_reg.scalar_one()
    
    # On force le rafraîchissement depuis la DB pour voir l'impact du trigger
    await session.refresh(reg_b)
    
    assert reg_b.statut == "confirmee"

@pytest.mark.asyncio
async def test_get_my_registrations(client: AsyncClient):
    """Vérifie la consultation de son propre agenda"""
    token, info = await create_fresh_user(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Inscription
    await client.post("/api/v1/events/2/register", json={"places_reservees": 1}, headers=headers)
    
    # Récupérer l'ID de l'utilisateur
    me_res = await client.get("/api/v1/auth/me", headers=headers)
    user_id = me_res.json()["id"]

    response = await client.get(f"/api/v1/users/{user_id}/registrations", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 1
    assert data["data"][0]["event"]["id"] == 2

@pytest.mark.asyncio
async def test_re_register_after_cancellation(client: AsyncClient):
    """Vérifie qu'un utilisateur peut se réinscrire après avoir annulé son inscription"""
    token, _ = await create_fresh_user(client)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Première inscription
    res1 = await client.post("/api/v1/events/2/register", json={"places_reservees": 1}, headers=headers)
    assert res1.status_code == 201
    assert res1.json()["statut"] == "confirmee"

    # 2. Annulation
    res2 = await client.delete("/api/v1/events/2/register", headers=headers)
    assert res2.status_code == 204

    # 3. Réinscription (doit réussir car la précédente a été annulée)
    res3 = await client.post("/api/v1/events/2/register", json={"places_reservees": 1}, headers=headers)
    assert res3.status_code == 201
    assert res3.json()["statut"] == "confirmee"
