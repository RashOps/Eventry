import pytest
import time
from httpx import AsyncClient
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
    # 1. On crée un utilisateur qui va saturer l'event (User A)
    token_a, _ = await create_fresh_user(client)
    # Event 1 a 9 places prises. On en prend 1. Total: 10/10.
    await client.post("/api/v1/events/1/register", json={"places_reservees": 1}, headers={"Authorization": f"Bearer {token_a}"})

    # 2. On crée un utilisateur qui va aller en liste d'attente (User B)
    token_b, info_b = await create_fresh_user(client)
    await client.post("/api/v1/events/1/register", json={"places_reservees": 1}, headers={"Authorization": f"Bearer {token_b}"})

    # 3. User A annule
    res_cancel = await client.delete("/api/v1/events/1/register", headers={"Authorization": f"Bearer {token_a}"})
    assert res_cancel.status_code == 204

    # 4. VÉRIFICATION DU TRIGGER : User B doit être promu
    stmt_u = select(Utilisateur).where(Utilisateur.email == info_b["email"])
    user_b = (await session.execute(stmt_u)).scalar_one()
    
    stmt_reg = select(Inscription).where(
        Inscription.id_utilisateur == user_b.id,
        Inscription.id_evenement == 1
    )
    reg_b = (await session.execute(stmt_reg)).scalar_one()
    
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
