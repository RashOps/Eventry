from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import text
from config import settings
import asyncio
from typing import AsyncGenerator

# 1. Modification du protocole : de 'postgresql://' à 'postgresql+asyncpg://'
DATABASE_URL = (
    f"postgresql+asyncpg://{settings.sql_user}:{settings.sql_password}"
    f"@{settings.sql_host}:{settings.sql_port}/{settings.sql_database}"
)

# 2. Création de l'engine Asynchrone avec configuration du Pool
async_engine = create_async_engine(
    DATABASE_URL,
    echo=False,              # Passe à True pour débugger les requêtes SQL générées
    pool_size=10,            # Nombre de connexions persistantes maintenues ouvertes
    max_overflow=20,         # Connexions temporaires max si le pool est saturé
    pool_timeout=30,         # Timeout si aucune connexion n'est dispo dans le pool
)

# 3. Factory pour générer des sessions asynchrones
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False  # Évite les requêtes de rafraîchissement implicites inutiles
)

# Context Manager Asynchrone pour un usage hors FastAPI (ex: scripts, cron)
async def get_async_sqldb() -> AsyncGenerator[AsyncSession, None]:
    """Provides an asynchronous SQLAlchemy session with automatic transaction management.

    Yields:
        AsyncSession: The active database session.

    Raises:
        Exception: If the transaction fails, executing a rollback before propagating.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            print(f"[Error] Transaction failed, rollback executed: {e}")
            raise

if __name__ == "__main__":
    async def main():
        # Utilisation de l'async context manager
        async for session in get_async_sqldb():
            # Pour du SQL brut, on utilise text() de SQLAlchemy
            query = text("SELECT * FROM tags;")
            result = await session.execute(query)
            
            # Récupération des records
            records = result.fetchall()
            print(f"Données récupérées en Async : {records}")

    # Lancement de la boucle pour le script autonome
    asyncio.run(main())