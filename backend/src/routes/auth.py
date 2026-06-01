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
from src.schemas.users import UserCreate, UserLogin, UserOut, Token, UserRole
from sqlalchemy import text

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserOut)
async def register(user_data: UserCreate, session: AsyncSession = Depends(get_async_sqldb)):
    """Crée un nouvel utilisateur. Si organisateur, crée aussi son profil pro via SQL."""
    
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

    # 2. Validation métier pour organisateur
    if user_data.role == UserRole.ORGANISATEUR and not user_data.nom_organisation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization name is required for organizer registration"
        )

    # 3. Hacher le mot de passe et créer l'instance de base
    new_user = Utilisateur(
        email=user_data.email,
        pseudo=user_data.pseudo,
        mot_de_passe_hash=hash_password(user_data.password)
    )

    # 4. Sauvegarder l'utilisateur (Phase 1)
    try:
        session.add(new_user)
        await session.flush() # Récupérer l'ID pour la procédure

        # 5. Si Organisateur : Appel à la procédure stockée SQL
        if user_data.role == UserRole.ORGANISATEUR:
            await session.execute(
                text("CALL proc_promouvoir_organisateur(:u_id, :org_name, :desc)"),
                {
                    "u_id": new_user.id,
                    "org_name": user_data.nom_organisation,
                    "desc": user_data.description_organisation
                }
            )
        
        await session.commit()
        await session.refresh(new_user)
        return new_user
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
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
