from fastapi import APIRouter, Depends
from pydantic import BaseModel

from egame179_backend.db.cycle import CycleDAO
from egame179_backend.db.cycle_params import CycleParams, CycleParamsDAO

router = APIRouter()


class CycleParamsPlayer(BaseModel):
    """Cycle params with player visible info."""

    alpha: float
    beta: float
    gamma: float
    tau_s: int


@router.get("/cycle_params", response_model=CycleParamsPlayer)
async def get_cycle_params(dao: CycleParamsDAO = Depends(), cycle_dao: CycleDAO = Depends()) -> CycleParams:
    """Get current cycle parameters, visible for player.

    Args:
        dao (CycleParamsDAO): cycle parameters table data access object.
        cycle_dao (CycleDAO): cycle table data access object.

    Returns:
        CycleParams: CycleParamsPlayer responce model.
    """
    current_cycle = await cycle_dao.get_cycle()
    return await dao.get_cycle_parameters(current_cycle.cycle)
