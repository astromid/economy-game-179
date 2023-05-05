from fastapi import APIRouter, Depends, Security

from egame179_backend.api.auth.dependencies import get_current_user
from egame179_backend.db.cycle import Cycle, CycleDAO

router = APIRouter()


@router.get("/info")
async def get_cycle(dao: CycleDAO = Depends()) -> Cycle:
    """Get current cycle information.

    Args:
        dao (CycleDAO): cycles table data access object.

    Returns:
        Cycle: current cycle info.
    """
    return await dao.get_cycle()


@router.get("/new", dependencies=[Security(get_current_user, scopes=["root"])])
async def create_cycle(dao: CycleDAO = Depends()) -> None:
    """Create new cycle.

    Args:
        dao (CycleDAO): cycles table data access object.
    """
    await dao.create_cycle()


@router.get("/start", dependencies=[Security(get_current_user, scopes=["root"])])
async def start_cycle(dao: CycleDAO = Depends()) -> None:
    """Start current cycle.

    Args:
        dao (CycleDAO): cycles table data access object.
    """
    await dao.start_cycle()


@router.get("/finish", dependencies=[Security(get_current_user, scopes=["root"])])
async def finish_cycle(dao: CycleDAO = Depends()) -> None:
    """Finish current cycle.

    Args:
        dao (CycleDAO): cycles table data access object.
    """
    await dao.finish_cycle()
