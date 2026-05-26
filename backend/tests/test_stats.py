import pytest
from httpx import AsyncClient
from src.models import RoleEnum

@pytest.mark.asyncio
async def test_get_event_stats(client: AsyncClient):
    """Vérifie les stats détaillées d'un événement (SQL + Mongo)"""
    # 1. Login Admin (Organisateur du seed pour l'event 1)
    login_payload = {"username": "admin@eventry.fr", "password": "password123"}
    login_res = await client.post("/api/v1/auth/login", data=login_payload)
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Récupérer les stats de l'event 1 (Nuit Électro)
    # Seed SQL : 9 places confirmées / Capacité 10
    # Seed Mongo : 2 avis (Note 4 et 5)
    response = await client.get("/api/v1/events/1/stats", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    
    # Vérification SQL
    assert data["event_id"] == 1
    assert data["registered_count"] == 10
    assert data["fill_rate"] == 100.0
    
    # Vérification MongoDB
    assert data["reviews"]["total"] >= 2
    assert data["reviews"]["average"] >= 4.0
    assert "distribution" in data["reviews"]
    assert data["reviews"]["average_by_criteria"]["ambiance"] > 0

@pytest.mark.asyncio
async def test_get_dashboard_global(client: AsyncClient):
    """Vérifie la vue globale du dashboard via la vue SQL complexe"""
    login_payload = {"username": "admin@eventry.fr", "password": "password123"}
    login_res = await client.post("/api/v1/auth/login", data=login_payload)
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/dashboard", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    
    assert "data" in data
    assert data["total_events"] >= 1
    # On vérifie que la vue SQL a bien remonté les colonnes attendues
    first_event = data["data"][0]
    assert "organisateur" in first_event
    assert "taux_remplissage" in first_event
    assert "ville" in first_event

@pytest.mark.asyncio
async def test_stats_unauthorized(client: AsyncClient):
    """Vérifie qu'un participant ne peut pas voir les stats d'un organisateur"""
    # Login Lucas (Participant)
    login_payload = {"username": "lucas@test.com", "password": "password123"}
    login_res = await client.post("/api/v1/auth/login", data=login_payload)
    token = login_res.json()["access_token"]
    
    # Tentative accès dashboard
    response = await client.get("/api/v1/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    
    # Tentative accès stats event 1
    response = await client.get("/api/v1/events/1/stats", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
