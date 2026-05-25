from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List

from src.utils.postegre_connexion import get_async_sqldb
from src.utils.security_jwt import get_current_user
from src.schemas.users import UserOut, UserUpdate

router = APIRouter(
    prefix="/users",
    tags=["User profil"],
)

@router.get("/{user_id}", response_model=UserOut)
async def retrieve_user_infos(user_id: int, session: AsyncSession = Depends(get_async_sqldb)):
    """Récupère les informations publiques d'un utilisateur"""
    query = text("SELECT id, email, pseudo, role, avatar_url, date_inscription, est_actif FROM utilisateurs WHERE id = :id")
    result = await session.execute(query, {"id": user_id})
    user = result.fetchone()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return UserOut(
        id=user.id,
        email=user.email,
        pseudo=user.pseudo,
        role=user.role,
        avatar_url=user.avatar_url,
        date_inscription=user.date_inscription,
        est_actif=user.est_actif
    )

@router.patch("/{user_id}", response_model=UserOut)
async def modify_user_infos(
    user_id: int, 
    update_data: UserUpdate,
    current_user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_sqldb)
):
    """Permet à un utilisateur de modifier son propre profil"""
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to modify this profile"
        )
    
    # Construction dynamique de la requête de mise à jour
    updates = []
    params = {"id": user_id}
    
    if update_data.pseudo is not None:
        updates.append("pseudo = :pseudo")
        params["pseudo"] = update_data.pseudo
    if update_data.avatar_url is not None:
        updates.append("avatar_url = :avatar_url")
        params["avatar_url"] = str(update_data.avatar_url)
        
    if not updates:
        return current_user

    query_str = f"UPDATE utilisateurs SET {', '.join(updates)} WHERE id = :id RETURNING id, email, pseudo, role, avatar_url, date_inscription, est_actif"
    
    try:
        result = await session.execute(text(query_str), params)
        updated_user = result.fetchone()
        return UserOut(
            id=updated_user.id,
            email=updated_user.email,
            pseudo=updated_user.pseudo,
            role=updated_user.role,
            avatar_url=updated_user.avatar_url,
            date_inscription=updated_user.date_inscription,
            est_actif=updated_user.est_actif
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Update failed: {str(e)}")

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_profil(
    user_id: int, 
    current_user: UserOut = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_sqldb)
):
    """Permet à un utilisateur de supprimer son compte"""
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this profile"
        )
        
    query = text("DELETE FROM utilisateurs WHERE id = :id")
    await session.execute(query, {"id": user_id})
    return None
