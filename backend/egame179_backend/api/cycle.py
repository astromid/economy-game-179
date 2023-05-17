from fastapi import APIRouter, Depends, Security

from egame179_backend.api.auth.dependencies import get_current_user
from egame179_backend.db.cycle import Cycle, CycleDAO

router = APIRouter()


@router.get("/current")
async def get_current(dao: CycleDAO = Depends()) -> Cycle:
    """Get current cycle information.

    Args:
        dao (CycleDAO): cycles table data access object.

    Returns:
        Cycle: current cycle info.
    """
    return await dao.get_current()


@router.get("/start", dependencies=[Security(get_current_user, scopes=["root"])])
async def start(dao: CycleDAO = Depends()) -> None:
    """Start current cycle.

    Args:
        dao (CycleDAO): cycles table data access object.
    """
    await dao.start()


@router.get("/finish", dependencies=[Security(get_current_user, scopes=["root"])])
async def finish(dao: CycleDAO = Depends()) -> None:
    """Finish current cycle.

    Args:
        dao (CycleDAO): cycles table data access object.
    """
    await dao.finish()
