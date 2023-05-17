from fastapi import APIRouter, Depends

from egame179_backend.db import CycleDAO
from egame179_backend.db.bulletin import Bulletin, BulletinDAO

router = APIRouter()


@router.get("/list")
async def get_bulletins(dao: BulletinDAO = Depends(), cycle_dao: CycleDAO = Depends()) -> list[Bulletin]:
    """Get transactions history for user.

    Args:
        dao (BulletinDAO): transactions table data access object.
        cycle_dao (CycleDAO): cycle table data access object.

    Returns:
        list[Transaction]: transactions history for user.
    """
    cycle = await cycle_dao.get_current()
    return await dao.select(cycle=cycle.id)
