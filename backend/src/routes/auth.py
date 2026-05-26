from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import Any

from src.utils.postegre_connexion import get_async_sqldb
from src.utils.security_jwt import(
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)
from src.models.users import Utilisateur
from src.schemas.users import UserCreate, UserLogin, UserOut, Token

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserOut)
async def register(user_data: UserCreate, session: AsyncSession = Depends(get_async_sqldb)):
    """Crée un nouvel utilisateur avec mot de passe haché (via SQLModel)"""
    
    # 1. Vérifier si l'utilisateur existe déjà
    statement = select(Utilisateur).where(
        (Utilisateur.email == user_data.email) | (Utilisateur.pseudo == user_data.pseudo)
    )
    result = await session.execute(statement)
    if result.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or Pseudo already registered"
        )

    # 2. Hacher le mot de passe et créer l'instance
    new_user = Utilisateur(
        email=user_data.email,
        pseudo=user_data.pseudo,
        mot_de_passe_hash=hash_password(user_data.password)
    )

    # 3. Sauvegarder en base
    try:
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

from fastapi.security import OAuth2PasswordRequestForm

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_async_sqldb)
):
    """Authentifie l'utilisateur et retourne un JWT (Compatible Swagger Authorize)"""
    
    # 1. Récupérer l'utilisateur (username dans le formulaire correspond à notre email)
    statement = select(Utilisateur).where(Utilisateur.email == form_data.username)
    result = await session.execute(statement)
    user = result.scalar_one_or_none()

    # 2. Vérifier mot de passe
    if not user or not verify_password(form_data.password, user.mot_de_passe_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Créer le token
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserOut)
async def get_my_profile(current_user: Utilisateur = Depends(get_current_user)):
    """Retourne le profil de l'utilisateur actuellement connecté"""
    return current_user

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(current_user: Utilisateur = Depends(get_current_user)):
    """Invalide la session actuelle (stateless)"""
    return None
