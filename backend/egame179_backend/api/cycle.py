from fastapi import APIRouter, Depends, Security

from egame179_backend.api.auth.dependencies import get_current_user
from egame179_backend.db import MarketDAO, MarketPriceDAO, SupplyDAO, TransactionDAO, WarehouseDAO, WorldDemandDAO
from egame179_backend.db.cycle import Cycle, CycleDAO
from egame179_backend.engine.mechanics import finish_cycle, prepare_cycle

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
async def finish(
    dao: CycleDAO = Depends(),
    market_dao: MarketDAO = Depends(),
    price_dao: MarketPriceDAO = Depends(),
    supply_dao: SupplyDAO = Depends(),
    transaction_dao: TransactionDAO = Depends(),
    wd_dao: WorldDemandDAO = Depends(),
    wh_dao: WarehouseDAO = Depends(),
) -> None:
    """Finish current cycle.

    Args:
        dao (CycleDAO): cycles table data access object.
        market_dao (MarketDAO): markets table data access object.
        price_dao (MarketPriceDAO): market_prices table data access object.
        supply_dao (SupplyDAO): supplies table data access object.
        transaction_dao (TransactionDAO): transactions table data access object.
        wd_dao (WorldDemandDAO): world_demands table data access object.
        wh_dao (WarehouseDAO): warehouses table data access object.
    """
    finished_cycle = await dao.finish()
    await finish_cycle(
        cycle=finished_cycle,
        market_dao=market_dao,
        price_dao=price_dao,
        supply_dao=supply_dao,
        transaction_dao=transaction_dao,
        wd_dao=wd_dao,
        wh_dao=wh_dao,
    )
    new_cycle = await dao.get_current()
    await prepare_cycle()
