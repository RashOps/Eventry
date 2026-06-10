from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import List

from src.utils.postegre_connexion import get_async_sqldb
from src.models import Categorie
from src.schemas.events import CategoryOut

router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)

@router.get("/", response_model=List[CategoryOut])
async def list_categories(session: AsyncSession = Depends(get_async_sqldb)) -> List[Categorie]:
    """Retrieves all registered event categories in the database.

    Args:
        session (AsyncSession): Database session dependency.

    Returns:
        List[Categorie]: A list of all categories.
    """
    statement = select(Categorie)
    result = await session.execute(statement)
    categories = result.scalars().all()
    return list(categories)
