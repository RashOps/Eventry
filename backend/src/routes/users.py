from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import List
from sqlalchemy import text

from src.utils.postegre_connexion import get_async_sqldb
from src.utils.security_jwt import get_current_user
from src.models.users import Utilisateur
from src.models.base import RoleEnum
from src.schemas.users import UserOut, UserUpdate, UserRole

router = APIRouter(
    prefix="/users",
    tags=["User profil"],
)

@router.get("/{user_id}", response_model=UserOut)
async def retrieve_user_infos(user_id: int, session: AsyncSession = Depends(get_async_sqldb)):
    """Récupère les informations publiques d'un utilisateur (via SQLModel)"""
    user = await session.get(Utilisateur, user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return user

@router.patch("/{user_id}", response_model=UserOut)
async def modify_user_infos(
    user_id: int, 
    update_data: UserUpdate,
    current_user: Utilisateur = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_sqldb)
):
    """Permet à un utilisateur de modifier son propre profil (via SQLModel)"""
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to modify this profile"
        )
    
    # Récupération de l'utilisateur à mettre à jour
    db_user = await session.get(Utilisateur, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Mise à jour sélective
    user_data = update_data.model_dump(exclude_unset=True)
    
    # Promotion organisateur si demandée et non déjà effective
    if "role" in user_data:
        if user_data["role"] == UserRole.ORGANISATEUR:
            if db_user.role != RoleEnum.organisateur:
                nom_org = user_data.get("nom_organisation")
                if not nom_org:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Organization name is required to become an organizer"
                    )
                desc_org = user_data.get("description_organisation")
                try:
                    await session.execute(
                        text("CALL proc_promouvoir_organisateur(:u_id, :org_name, :desc)"),
                        {
                            "u_id": db_user.id,
                            "org_name": nom_org,
                            "desc": desc_org
                        }
                    )
                    await session.commit()
                    await session.refresh(db_user)
                except Exception as e:
                    await session.rollback()
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Failed to promote user to organizer: {str(e)}"
                    )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Changing role to something other than organizer is not supported"
            )
            
    # Mise à jour des autres champs (pseudo, avatar_url)
    for key, value in user_data.items():
        if key in ["role", "nom_organisation", "description_organisation"]:
            continue  # Gérés par la procédure stockée ci-dessus
        if key == "avatar_url":
            setattr(db_user, key, str(value) if value else None)
        else:
            setattr(db_user, key, value)
    
    try:
        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)
        return db_user
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Update failed: {str(e)}")

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_profil(
    user_id: int, 
    current_user: Utilisateur = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_sqldb)
):
    """Permet à un utilisateur de supprimer son compte (via SQLModel)"""
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this profile"
        )
        
    db_user = await session.get(Utilisateur, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    await session.delete(db_user)
    await session.commit()
    return None
