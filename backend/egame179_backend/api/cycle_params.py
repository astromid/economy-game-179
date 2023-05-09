import math

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from egame179_backend.db.cycle import CycleDAO
from egame179_backend.db.cycle_params import CycleParams, CycleParamsDAO
from egame179_backend.db.market import MarketDAO

router = APIRouter()


class CycleParamsPlayer(BaseModel):
    """Cycle params with player visible info."""

    alpha: float
    beta: float
    gamma: float
    tau_s: int


class DemandFactor(BaseModel):
    """Demand factors for each market."""

    market_id: int
    factor: float


@router.get("/params", response_model=CycleParamsPlayer)
async def get_cycle_params(dao: CycleParamsDAO = Depends(), cycle_dao: CycleDAO = Depends()) -> CycleParams:
    """Get current cycle parameters, visible for player.

    Args:
        dao (CycleParamsDAO): cycle parameters table data access object.
        cycle_dao (CycleDAO): cycle table data access object.

    Returns:
        CycleParams: CycleParamsPlayer responce model.
    """
    current_cycle = await cycle_dao.get_current()
    return await dao.get(current_cycle.cycle)


@router.get("/demand_factors")
async def get_demand_factors(
    dao: CycleParamsDAO = Depends(),
    cycle_dao: CycleDAO = Depends(),
    market_dao: MarketDAO = Depends(),
) -> list[DemandFactor]:
    """Get current market demand factors.

    Args:
        dao (CycleParamsDAO): cycle parameters table data access object.
        cycle_dao (CycleDAO): cycle table data access object.
        market_dao (MarketDAO): market table data access object.

    Raises:
        ValueError: incorrect market ring.

    Returns:
        list[DemandFactors]: demand factors for each market.
    """
    current_cycle = await cycle_dao.get_current()
    cycle_params = await dao.get(current_cycle.cycle)
    initial_cycle_params = await dao.get(cycle=1)
    markets = await market_dao.get()

    demand_factors = []
    for market in markets:
        match market.ring:
            case 0:
                demand = cycle_params.demand_ring0
                initial_demand = initial_cycle_params.demand_ring0
            case 1:
                demand = cycle_params.demand_ring1
                initial_demand = initial_cycle_params.demand_ring1
            case 2:
                demand = cycle_params.demand_ring2
                initial_demand = initial_cycle_params.demand_ring2
            case _:
                raise ValueError(f"Incorrect {market.ring = }")
        demand_factors.append(DemandFactor(market_id=market.id, factor=math.log(demand / initial_demand) + 1))
    return demand_factors
