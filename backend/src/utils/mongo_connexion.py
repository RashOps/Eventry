from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from config import settings

from src.models.nosql.events import EventsCatalog
from src.models.nosql.reviews import Avis

async def init_db_nosql() -> None:
    """Initializes the asynchronous MongoDB connection and registers Beanie documents.

    Registers:
        EventsCatalog: The MongoDB event catalog collection.
        Avis: The reviews and community feedback collection.
    """
    # 1. Création du client Motor
    client = AsyncIOMotorClient(settings.mongo_uri)
    
    # 2. Initialisation de Beanie avec la liste des documents
    await init_beanie(
        database=client[settings.mongo_db_name],
        document_models=[
            EventsCatalog,
            Avis
        ]
    )
    
    print(f"✅ MongoDB Async (Motor + Beanie) initialisé sur : {settings.mongo_db_name}")

def get_motor_client() -> AsyncIOMotorClient:
    """Returns the raw asynchronous Motor client for low-level MongoDB queries.

    Returns:
        AsyncIOMotorClient: The raw Motor connection client.
    """
    return AsyncIOMotorClient(settings.mongo_uri)
