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
    prefix="/auth",
    tags=["Authentication"],
    responses={404: {"description": "Unable to create or login user"}},
)

# Registration API
@router.post("/register")
async def register(pseudo: str, email: str, password: str, role: str = "participant"):
    try:
        CREATE_USER_QUERY = f"INSERT INTO utilisateurs VALUES ({email.lower()}, {password}, {pseudo}, {role.lower});"
        asyncio.run(execute_query(CREATE_USER_QUERY))
    except Exception as e:
        raise Exception(f"Message: {e}")
    
@router.post("/login")
def login(email: str, password: str):
    USER = {
        "user_email" : email,
        "user_passorwd" : password
    }
    try:
        RETRIEVE_USER = f"SELECT * FROM utilisateurs WHERE email == {USER['user_email']} AND password == {USER['user_passorwd']}"
        asyncio.run(execute_query(RETRIEVE_USER))
    except Exception as e:
        raise Exception(f"Message: {e}")


@router.post("/logout")
def logout():
    pass

@router.get("/me")
def get_profil():
    pass