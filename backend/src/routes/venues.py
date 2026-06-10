from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import List

from src.utils.postegre_connexion import get_async_sqldb
from src.models import Lieu
from src.schemas.events import VenueDetail

router = APIRouter(
    prefix="/venues",
    tags=["Venues"],
)

@router.get("/", response_model=List[VenueDetail])
async def list_venues(session: AsyncSession = Depends(get_async_sqldb)) -> List[Lieu]:
    """Retrieves all registered venues in the database.

    Args:
        session (AsyncSession): Database session dependency.

    Returns:
        List[Lieu]: A list of all venues.
    """
    statement = select(Lieu)
    result = await session.execute(statement)
    venues = result.scalars().all()
    return list(venues)
