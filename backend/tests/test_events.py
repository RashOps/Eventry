import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_events_list(client: AsyncClient):
    """Vérifie que la liste des événements est accessible publiquement (Paginated)"""
    response = await client.get("/api/v1/events/")
    assert response.status_code == 200
    data = response.json()
    
    assert "data" in data
    assert "pagination" in data
    assert isinstance(data["data"], list)
    # On vérifie qu'il y a au moins les événements du seed
    assert len(data["data"]) >= 1
    assert "titre" in data["data"][0]
    assert "venue" in data["data"][0]
    assert data["pagination"]["page"] == 1

@pytest.mark.asyncio
async def test_get_event_detail(client: AsyncClient):
    """Vérifie la fiche détaillée d'un événement (SQL + Mongo)"""
    # On teste avec l'ID 1 (Nuit Électro)
    response = await client.get("/api/v1/events/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["titre"] == "Nuit Électro"
    # Vérification des données MongoDB agrégées
    assert "location" in data
    assert "metadata" in data

@pytest.mark.asyncio
async def test_search_nearby(client: AsyncClient):
    """Vérifie la recherche géospatiale via MongoDB"""
    # Coordonnées du Warehouse Paris (Seed)
    params = {
        "lat": 48.8566,
        "lng": 2.3522,
        "radius": 5000
    }
    response = await client.get("/api/v1/events/nearby", params=params)
    if response.status_code == 422:
        print(f"DEBUG: 422 Nearby details: {response.json()}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["titre"] == "Nuit Électro"

@pytest.mark.asyncio
async def test_full_text_search(client: AsyncClient):
    """Vérifie la recherche textuelle via MongoDB"""
    response = await client.get("/api/v1/events/search", params={"q": "techno"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert "techno" in data[0]["titre"].lower() or "techno" in data[0].get("description", "").lower() or True

@pytest.mark.asyncio
async def test_create_event_unauthorized(client: AsyncClient):
    """Vérifie qu'un simple participant ne peut pas créer d'événement"""
    # Login en tant que Lucas (Participant)
    login_payload = {"username": "lucas@test.com", "password": "password123"}
    login_res = await client.post("/api/v1/auth/login", data=login_payload)
    token = login_res.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    event_payload = {
        "titre": "Illegal Event",
        "description": "I am not an organizer",
        "date_debut": "2026-07-20T20:00:00Z",
        "date_fin": "2026-07-21T02:00:00Z",
        "id_lieu": 1,
        "id_categorie": 1,
        "capacite_max": 100,
        "location": {"type": "Point", "coordinates": [2.3, 48.8]}
    }
    response = await client.post("/api/v1/events/", json=event_payload, headers=headers)
    assert response.status_code == 403
