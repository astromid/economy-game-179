from fastapi import APIRouter, Depends, Security

from egame179_backend.api.auth.dependencies import get_current_user
from egame179_backend.db import CycleDAO
from egame179_backend.db.modificators import Modificator, ModificatorDAO
from egame179_backend.db.user import User

router = APIRouter()


@router.get("/list/user")
async def get_user_modificators(
    user: User = Depends(get_current_user),
    dao: ModificatorDAO = Depends(),
    cycle_dao: CycleDAO = Depends(),
) -> list[Modificator]:
    """Get user modificators.

    Args:
        user (User): authenticated user data.
        dao (ModificatorDAO): modificators table data access object.
        cycle_dao (CycleDAO): cycles table data access object.

    Returns:
        list[Modificator]: user modificators.
    """
    cycle = await cycle_dao.get_current()
    return await dao.select(cycle=cycle.id, user=user.id)


@router.get("/list", dependencies=[Security(get_current_user, scopes=["root"])])
async def get_modificators(dao: ModificatorDAO = Depends(), cycle_dao: CycleDAO = Depends()) -> list[Modificator]:
    """Get modificators for all users.

    Args:
        dao (ModificatorDAO): modificators table data access object.
        cycle_dao (CycleDAO): cycles table data access object.

    Returns:
        list[Modificator]: modificators for all users.
    """
    cycle = await cycle_dao.get_current()
    return await dao.select(cycle=cycle.id)
