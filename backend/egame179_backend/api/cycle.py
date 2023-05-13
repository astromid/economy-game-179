from fastapi import APIRouter, Depends, Security

from egame179_backend.api.auth.dependencies import get_current_user
from egame179_backend.db import (
    BalanceDAO,
    CycleParamsDAO,
    MarketDAO,
    PriceDAO,
    ProductDAO,
    SupplyDAO,
    TransactionDAO,
    UnlockedMarketDAO,
)
from egame179_backend.db.cycle import Cycle, CycleDAO
from egame179_backend.engine import create_cycle, finish_cycle

router = APIRouter()


@router.get("/current")
async def get_current_cycle(dao: CycleDAO = Depends()) -> Cycle:
    """Get current cycle information.

    Args:
        dao (CycleDAO): cycles table data access object.

    Returns:
        Cycle: current cycle info.
    """
    return await dao.get_current()


@router.get("/new", dependencies=[Security(get_current_user, scopes=["root"])])
async def create(
    dao: CycleDAO = Depends(),
    cycle_params_dao: CycleParamsDAO = Depends(),
    price_dao: PriceDAO = Depends(),
    transaction_dao: TransactionDAO = Depends(),
    market_dao: MarketDAO = Depends(),
    product_dao: ProductDAO = Depends(),
    balance_dao: BalanceDAO = Depends(),
    unlocked_market_dao: UnlockedMarketDAO = Depends(),
) -> None:
    """Create new cycle.

    Args:
        dao (CycleDAO): cycles table data access object.
    """
    await dao.create()
    cycle = await dao.get_current()
    await create_cycle(
        cycle=cycle.cycle,
        market_dao=market_dao,
        cycle_params_dao=cycle_params_dao,
        price_dao=price_dao,
        transaction_dao=transaction_dao,
        product_dao=product_dao,
        balance_dao=balance_dao,
        unlocked_market_dao=unlocked_market_dao,
    )


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
    supply_dao: SupplyDAO = Depends(),
    market_dao: MarketDAO = Depends(),
    cycle_params_dao: CycleParamsDAO = Depends(),
    price_dao: PriceDAO = Depends(),
    balance_dao: BalanceDAO = Depends(),
    transaction_dao: TransactionDAO = Depends(),
    product_dao: ProductDAO = Depends(),
) -> None:
    """Finish current cycle.

    Args:
        dao (CycleDAO): cycles table data access object.
    """
    await dao.finish()
    cycle = await dao.get_current()
    await finish_cycle(
        cycle=cycle,
        supply_dao=supply_dao,
        market_dao=market_dao,
        cycle_params_dao=cycle_params_dao,
        price_dao=price_dao,
        balance_dao=balance_dao,
        transaction_dao=transaction_dao,
        product_dao=product_dao,
    )
