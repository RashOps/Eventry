from pymongo import MongoClient
from pymongo.database import Database

from config import settings

_client: MongoClient | None = None

def get_db_nosql() -> Database:
    """
    Returns the MongoDB Database object via lazy initialization.

    Returns:
        Database: PyMongo database instance.

    Raises:
        Exception: If connection to MongoDB fails.
    """
    global _client

    if _client is None:
        try:
            _client = MongoClient(settings.mongo_uri)
            _client.admin.command('ping')
        except Exception as e:
            raise Exception(f"Message: {e}")

    return _client[settings.mongo_db_name]

if __name__ == "__main__":
    db = get_db_nosql()
    avis = db["avis"]
    cursor = avis.find({})
    for element in cursor:
        print(element)