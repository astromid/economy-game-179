from fastapi import APIRouter, Depends, Security

from egame179_backend.api.auth.dependencies import get_current_user
from egame179_backend.db import CycleDAO
from egame179_backend.db.modificators import FeeModificator, FeeModificatorDAO
from egame179_backend.db.user import User

router = APIRouter()


@router.get("/list")
async def get_user_modificators(
    user: User = Depends(get_current_user),
    dao: FeeModificatorDAO = Depends(),
    cycle_dao: CycleDAO = Depends(),
) -> list[FeeModificator]:
    """Get user modificators.

    Args:
        user (User): authenticated user data.
        dao (FeeModificatorDAO): modificators table data access object.
        cycle_dao (CycleDAO): cycles table data access object.

    Returns:
        list[Modificator]: user modificators.
    """
    cycle = await cycle_dao.get_current()
    return await dao.select(cycle=cycle.id, user=user.id)


@router.get("/list/all", dependencies=[Security(get_current_user, scopes=["root"])])
async def get_modificators(
    dao: FeeModificatorDAO = Depends(),
    cycle_dao: CycleDAO = Depends(),
) -> list[FeeModificator]:
    """Get modificators for all users.

    Args:
        dao (FeeModificatorDAO): modificators table data access object.
        cycle_dao (CycleDAO): cycles table data access object.

    Returns:
        list[Modificator]: modificators for all users.
    """
    cycle = await cycle_dao.get_current()
    return await dao.select(cycle=cycle.id)


@router.post("/new", dependencies=[Security(get_current_user, scopes=["root"])])
async def create_modificator(modificator: FeeModificator, dao: FeeModificatorDAO = Depends()) -> None:
    """Create new modificator.

    Args:
        modificator (FeeModificator): modificator data.
        dao (FeeModificatorDAO): modificators table data access object.
    """
    await dao.create(
        cycle=modificator.cycle,
        user=modificator.user,
        fee=modificator.fee,
        coeff=modificator.coeff,
    )
