import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool
from sqlmodel import SQLModel
from typing import AsyncGenerator

from src.main import app
from src.utils.postegre_connexion import get_async_sqldb
from src.utils.mongo_connexion import init_db_nosql
from config import settings

# --- Configuration de la DB de TEST ---
# Utilisation de NullPool pour éviter les erreurs "another operation in progress" avec asyncpg
TEST_DATABASE_URL = f"postgresql+asyncpg://{settings.sql_user}:{settings.sql_password}@{settings.sql_host}:{settings.sql_port}/{settings.sql_database}"

test_engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
TestSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)

@pytest_asyncio.fixture(scope="function")
async def session() -> AsyncGenerator[AsyncSession, None]:
    """Donne une session SQL isolée pour chaque test avec Rollback automatique"""
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()

@pytest_asyncio.fixture(scope="function")
async def client(session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Client HTTP asynchrone qui injecte la session de test"""
    # Initialisation Beanie pour les tests
    await init_db_nosql()
    
    async def override_get_async_sqldb():
        yield session

    app.dependency_overrides[get_async_sqldb] = override_get_async_sqldb
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test", follow_redirects=True) as ac:
        yield ac
    app.dependency_overrides.clear()
