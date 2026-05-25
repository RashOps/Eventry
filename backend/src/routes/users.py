from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text
import asyncio

from src.utils.mongo_connexion import get_db_nosql
from src.utils.postegre_connexion import get_async_sqldb
from src.utils.security_jwt import(
    hash_password,
    verify_password,
    create_access_token
)

# DB Connexion - Excecute query
async def execute_query(query_to_exceute: str, option: str = None):
        async for session in get_async_sqldb():
            query = text(query_to_exceute)
            result = await session.execute(query)
            
            if option == "result":
                # Récupération des records
                records = result.fetchall()
                return records
            
# Router for connexion
router = APIRouter(
    prefix="/users",
    tags=["User profil"],
    responses={404: {"description": "Unable to retrieve or delete user infos"}},
)

@router.get("/{:id}")
def retrieve_user_infos():
    pass

@router.patch("/{:id}")
def modify_user_infos():
    pass

@router.delete("/{:id}")
def delete_user_profil():
    pass