from fastapi import APIRouter, Depends, Security

from egame179_backend import db
from egame179_backend.api.auth.dependencies import get_current_user
from egame179_backend.db.cycle import Cycle, CycleDAO
from egame179_backend.engine.mechanics import finish_cycle, prepare_new_cycle

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
async def finish(  # noqa: WPS211
    dao: CycleDAO = Depends(),
    balance_dao: db.BalanceDAO = Depends(),
    market_dao: db.MarketDAO = Depends(),
    production_dao: db.ProductionDAO = Depends(),
    price_dao: db.MarketPriceDAO = Depends(),
    stock_dao: db.StockDAO = Depends(),
    supply_dao: db.SupplyDAO = Depends(),
    theta_dao: db.ThetaDAO = Depends(),
    transaction_dao: db.TransactionDAO = Depends(),
    wh_dao: db.WarehouseDAO = Depends(),
    wd_dao: db.WorldDemandDAO = Depends(),
) -> None:
    """Finish current cycle.

    Args:
        dao (CycleDAO): cycles table data access object.
        balance_dao (BalanceDAO): balances table data access object.
        market_dao (MarketDAO): markets table data access object.
        production_dao (ProductionDAO): productions table data access object.
        price_dao (MarketPriceDAO): market_prices table data access object.
        stock_dao (StockDAO): stocks table data access object.
        supply_dao (SupplyDAO): supplies table data access object.
        theta_dao (ThetaDAO): thetas table data access object.
        transaction_dao (TransactionDAO): transactions table data access object.
        wh_dao (WarehouseDAO): warehouses table data access object.
        wd_dao (WorldDemandDAO): world_demands table data access object.
    """
    finished_cycle = await dao.finish()
    await finish_cycle(
        cycle=finished_cycle,
        balance_dao=balance_dao,
        market_dao=market_dao,
        price_dao=price_dao,
        supply_dao=supply_dao,
        transaction_dao=transaction_dao,
        wd_dao=wd_dao,
        wh_dao=wh_dao,
    )
    await prepare_new_cycle(
        cycle=finished_cycle,
        balance_dao=balance_dao,
        market_dao=market_dao,
        price_dao=price_dao,
        production_dao=production_dao,
        supply_dao=supply_dao,
        stock_dao=stock_dao,
        theta_dao=theta_dao,
        transaction_dao=transaction_dao,
        wh_dao=wh_dao,
        wd_dao=wd_dao,
    )
