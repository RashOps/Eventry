import pytest
from httpx import AsyncClient
from src.models.users import Utilisateur
from sqlmodel import select

import time

@pytest.mark.asyncio
async def test_register_user(client: AsyncClient, session):
    """Vérifie l'inscription d'un nouvel utilisateur"""
    ts = int(time.time())
    payload = {
        "email": f"user_{ts}@test.com",
        "pseudo": f"Tester_{ts}",
        "password": "password123"
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    
    if response.status_code != 201:
        print(f"DEBUG: Response content: {response.json()}")
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["pseudo"] == payload["pseudo"]
    assert "id" in data
    
    # Vérifier en base que le mot de passe est bien haché
    stmt = select(Utilisateur).where(Utilisateur.email == payload["email"])
    result = await session.execute(stmt)
    user = result.scalar_one()
    assert user.mot_de_passe_hash != payload["password"]
    assert user.mot_de_passe_hash.startswith("$2b$")

@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """Vérifie que l'on ne peut pas s'inscrire avec un email déjà existant"""
    payload = {
        "email": "admin@eventry.fr", # Déjà dans le seed
        "pseudo": "AnotherPseudo",
        "password": "password123"
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409
    assert "already registered" in response.json()["detail"]

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """Vérifie la connexion avec des identifiants valides"""
    # Note: On utilise les identifiants du seed data
    payload = {
        "username": "admin@eventry.fr",
        "password": "password123"
    }
    # Swagger Authorize envoie du form-data
    response = await client.post("/api/v1/auth/login", data=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    """Vérifie l'échec de connexion avec un mauvais mot de passe"""
    payload = {
        "username": "admin@eventry.fr",
        "password": "wrongpassword"
    }
    response = await client.post("/api/v1/auth/login", data=payload)
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_me_protected(client: AsyncClient):
    """Vérifie l'accès à la route protégée /me"""
    # 1. Sans token
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401
    
    # 2. Avec token valide
    login_payload = {"username": "admin@eventry.fr", "password": "password123"}
    login_res = await client.post("/api/v1/auth/login", data=login_payload)
    token = login_res.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.get("/api/v1/auth/me", headers=headers)
    
    assert response.status_code == 200
    assert response.json()["email"] == "admin@eventry.fr"
