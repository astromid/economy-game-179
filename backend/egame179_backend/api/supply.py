import math
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Security
from pydantic import BaseModel

from egame179_backend import engine
from egame179_backend.api.auth.dependencies import get_current_user
from egame179_backend.db import BalanceDAO, CycleDAO, CycleParamsDAO, MarketDAO, ProductDAO, TransactionDAO
from egame179_backend.db.supply import Supply, SupplyDAO
from egame179_backend.db.user import User

router = APIRouter()


class SupplyBid(BaseModel):
    """Supply bid model."""

    market_id: int
    amount: int


@router.get("/user")
async def get_user_supplies(
    user: User = Depends(get_current_user),
    dao: SupplyDAO = Depends(),
    cycle_dao: CycleDAO = Depends(),
    cycle_params_dao: CycleParamsDAO = Depends(),
    market_dao: MarketDAO = Depends(),
) -> list[Supply]:
    """Get current supplies for user.

    Args:
        user (User): authenticated user data.
        dao (SupplyDAO): supplies table data access object.
        cycle_dao (CycleDAO): cycle table data access object.
        cycle_params_dao (CycleParamsDAO): cycle params table data access object.
        market_dao (MarketDAO): market table data access object.

    Returns:
        list[Supply]: current supplies for user.
    """
    current_ts = datetime.now()
    current_cycle = await cycle_dao.get_current()
    current_cycle_params = await cycle_params_dao.get(current_cycle.cycle)
    markets = await market_dao.get_all()
    supplies = await dao.get(cycle=current_cycle.cycle, user_id=user.id)

    velocities = engine.get_velocities(
        m_id2ring={market.id: market.ring for market in markets},
        cycle_params=current_cycle_params,
    )
    for supply in supplies:
        if supply.amount == 0:
            delivery_time = (current_ts - supply.ts_start).total_seconds()
            delivered_amount = math.floor(velocities[supply.market_id] * delivery_time)
            supply.amount = min(supply.declared_amount, delivered_amount)
    return supplies


@router.get("/all", dependencies=[Security(get_current_user, scopes=["root"])])
async def get_all_supplies(
    dao: SupplyDAO = Depends(),
    cycle_dao: CycleDAO = Depends(),
    cycle_params_dao: CycleParamsDAO = Depends(),
    market_dao: MarketDAO = Depends(),
) -> list[Supply]:
    """Get products history for all users.

    Args:
        dao (SupplyDAO): supplies table data access object.
        cycle_dao (CycleDAO): cycle table data access object.
        cycle_params_dao (CycleParamsDAO): cycle params table data access object.
        market_dao (MarketDAO): market table data access object.

    Returns:
        list[Supply]: current supplies for all users.
    """
    # TODO: refactor to avoid code duplication
    current_ts = datetime.now()
    current_cycle = await cycle_dao.get_current()
    current_cycle_params = await cycle_params_dao.get(current_cycle.cycle)
    markets = await market_dao.get_all()
    supplies = await dao.get(cycle=current_cycle.cycle)

    velocities = engine.get_velocities(
        m_id2ring={market.id: market.ring for market in markets},
        cycle_params=current_cycle_params,
    )
    for supply in supplies:
        if supply.amount == 0:
            delivery_time = (current_ts - supply.ts_start).total_seconds()
            delivered_amount = math.floor(velocities[supply.market_id] * delivery_time)
            supply.amount = min(supply.declared_amount, delivered_amount)
    return supplies


@router.post("/make")
async def make_supply(
    bid: SupplyBid,
    user: User = Depends(get_current_user),
    dao: SupplyDAO = Depends(),
    cycle_dao: CycleDAO = Depends(),
    cycle_params_dao: CycleParamsDAO = Depends(),
    product_dao: ProductDAO = Depends(),
    balance_dao: BalanceDAO = Depends(),
    transaction_dao: TransactionDAO = Depends(),
) -> None:
    """Make supply route.

    Args:
        bid (SupplyBid): supply bid.
        user (User): auth user.
        dao (SupplyDAO): supplies table data access object.
        cycle_dao (CycleDAO): cycle table data access object.
        cycle_params_dao (CycleParamsDAO): cycle params table data access object.
        product_dao (ProductDAO): products table data access object.
        balance_dao (BalanceDAO): balances table DAO.
        transaction_dao (TransactionDAO): transactions table DAO.

    Raises:
        HTTPException: amount <= 0
    """
    if bid.amount <= 0:
        raise HTTPException(status_code=400, detail=f"Incorrect {bid.amount = }")
    current_cycle = await cycle_dao.get_current()
    current_cycle_params = await cycle_params_dao.get(current_cycle.cycle)
    product = await product_dao.get(cycle=current_cycle.cycle, user_id=user.id, market_id=bid.market_id)
    supply_success = await engine.make_supply(
        cycle=current_cycle.cycle,
        user_id=user.id,
        market_id=bid.market_id,
        amount=bid.amount,
        storage=product.storage,
        beta=current_cycle_params.beta,
        balance_dao=balance_dao,
        transaction_dao=transaction_dao,
        supply_dao=dao,
    )
    if supply_success:
        product.storage -= bid.amount
        await product_dao.add(product)
