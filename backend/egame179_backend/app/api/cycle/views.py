from fastapi import APIRouter, Depends, Security

from egame179_backend.app.api.auth.dependencies import get_current_user
from egame179_backend.db.dao.cycles import CycleDAO
from egame179_backend.db.models import Cycle

router = APIRouter()


@router.get("/current", dependencies=[Security(get_current_user)])
async def get_current_cycle(cycle_dao: CycleDAO = Depends()) -> Cycle:
    """Get current cycle information.

    Args:
        cycle_dao (CycleDAO): cycles table data access object.

    Returns:
        Cycle: current cycle info.
    """
    return await cycle_dao.get_current_cycle()


@router.get("/finish", dependencies=[Security(get_current_user, scopes=["root"])])
async def finish_cycle(cycle_dao: CycleDAO = Depends()) -> None:
    """Finish current cycle.

    Args:
        cycle_dao (CycleDAO): cycles table data access object.
    """
    await cycle_dao.finish_current_cycle()


@router.get("/new", dependencies=[Security(get_current_user, scopes=["root"])])
async def start_cycle(cycle_dao: CycleDAO = Depends()) -> None:
    """Start new cycle.

    Args:
        cycle_dao (CycleDAO): cycles table data access object.
    """
    await cycle_dao.start_new_cycle()
