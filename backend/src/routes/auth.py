from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Any

from src.utils.postegre_connexion import get_async_sqldb
from src.utils.security_jwt import(
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)
from src.schemas.users import UserCreate, UserLogin, UserOut, Token

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserOut)
async def register(user_data: UserCreate, session: AsyncSession = Depends(get_async_sqldb)):
    """Crée un nouvel utilisateur avec mot de passe haché"""
    
    # 1. Vérifier si l'utilisateur existe déjà
    check_query = text("SELECT id FROM utilisateurs WHERE email = :email OR pseudo = :pseudo")
    existing_user = await session.execute(check_query, {"email": user_data.email, "pseudo": user_data.pseudo})
    if existing_user.fetchone():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or Pseudo already registered"
        )

    # 2. Hacher le mot de passe
    hashed_pwd = hash_password(user_data.password)

    # 3. Insérer en base
    insert_query = text(
        "INSERT INTO utilisateurs (email, mot_de_passe_hash, pseudo) "
        "VALUES (:email, :pwd, :pseudo) RETURNING id, email, pseudo, role, avatar_url, date_inscription, est_actif"
    )
    try:
        result = await session.execute(insert_query, {
            "email": user_data.email,
            "pwd": hashed_pwd,
            "pseudo": user_data.pseudo
        })
        new_user = result.fetchone()
        return UserOut(
            id=new_user.id,
            email=new_user.email,
            pseudo=new_user.pseudo,
            role=new_user.role,
            avatar_url=new_user.avatar_url,
            date_inscription=new_user.date_inscription,
            est_actif=new_user.est_actif
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, session: AsyncSession = Depends(get_async_sqldb)):
    """Authentifie l'utilisateur et retourne un JWT"""
    
    # 1. Récupérer l'utilisateur
    query = text("SELECT email, mot_de_passe_hash FROM utilisateurs WHERE email = :email")
    result = await session.execute(query, {"email": credentials.email})
    user = result.fetchone()

    # 2. Vérifier mot de passe
    if not user or not verify_password(credentials.password, user.mot_de_passe_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Créer le token
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(current_user: UserOut = Depends(get_current_user)):
    """
    Invalide la session actuelle.
    Note : Avec JWT (Stateless), la déconnexion réelle se fait côté client 
    en supprimant le token. Pour une invalidation côté serveur, il faudrait 
    implémenter une Blacklist (ex: Redis).
    """
    return None


@router.get("/me", response_model=UserOut)
async def get_my_profile(current_user: UserOut = Depends(get_current_user)):
    """Retourne le profil de l'utilisateur actuellement connecté"""
    return current_user