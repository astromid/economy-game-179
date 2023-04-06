from fastapi import APIRouter, Depends, Security

from egame179_backend.app.api.auth.dependencies import get_current_user
from egame179_backend.db.dao import CycleDAO
from egame179_backend.db.models import Cycle

router = APIRouter()


@router.get("/current", dependencies=[Security(get_current_user)])
async def get_current_cycle(dao: CycleDAO = Depends()) -> Cycle:
    """Get current cycle information.

    Args:
        dao (CycleDAO): cycles table data access object.

    Returns:
        Cycle: current cycle info.
    """
    return await dao.get_current_cycle()


@router.get("/finish", dependencies=[Security(get_current_user, scopes=["root"])])
async def finish_cycle(dao: CycleDAO = Depends()) -> None:
    """Finish current cycle.

    Args:
        dao (CycleDAO): cycles table data access object.
    """
    await dao.finish_current_cycle()


@router.get("/new", dependencies=[Security(get_current_user, scopes=["root"])])
async def start_cycle(dao: CycleDAO = Depends()) -> None:
    """Start new cycle.

    Args:
        dao (CycleDAO): cycles table data access object.
    """
    await dao.start_new_cycle()
