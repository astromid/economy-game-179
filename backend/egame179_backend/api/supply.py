from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Security
from pydantic import BaseModel

from egame179_backend.api.auth.dependencies import get_current_user
from egame179_backend.db import BulletinDAO, CycleDAO, MarketDAO, TransactionDAO, UserDAO, WarehouseDAO, WorldDemandDAO
from egame179_backend.db.supply import Supply, SupplyDAO
from egame179_backend.db.user import User
from egame179_backend.engine.math import bulletin_quantity, delivered_items
from egame179_backend.engine.utility import check_storage, get_market_names, get_supply_velocities

router = APIRouter()


class SupplyBid(BaseModel):
    """Supply bid model."""

    market: int
    quantity: int


@router.get("/list")
async def get_user_supplies(
    user: User = Depends(get_current_user),
    dao: SupplyDAO = Depends(),
    cycle_dao: CycleDAO = Depends(),
    market_dao: MarketDAO = Depends(),
    wd_dao: WorldDemandDAO = Depends(),
) -> list[Supply]:
    """Get current supplies for user.

    Args:
        user (User): authenticated user data.
        dao (SupplyDAO): supplies table data access object.
        cycle_dao (CycleDAO): cycle table data access object.
        market_dao (MarketDAO): market table data access object.
        wd_dao (WorldDemandDAO): world_demand table DAO.

    Returns:
        list[Supply]: current supplies for user.
    """
    ts = datetime.now()
    cycle = await cycle_dao.get_current()
    supplies = await dao.select(cycle=cycle.id, user=user.id)
    velocities = await get_supply_velocities(market_dao=market_dao, wd_dao=wd_dao, cycle=cycle.id, tau_s=cycle.tau_s)
    for supply in supplies:
        if supply.delivered == 0:
            supply.delivered = delivered_items(
                ts_start=supply.ts_start,
                ts_finish=ts,
                velocity=velocities[supply.market],
                quantity=supply.quantity,
            )
    return supplies


@router.get("/list/all", dependencies=[Security(get_current_user, scopes=["root"])])
async def get_all_supplies(
    dao: SupplyDAO = Depends(),
    cycle_dao: CycleDAO = Depends(),
    market_dao: MarketDAO = Depends(),
    wd_dao: WorldDemandDAO = Depends(),
) -> list[Supply]:
    """Get products history for all users.

    Args:
        dao (SupplyDAO): supplies table data access object.
        cycle_dao (CycleDAO): cycle table data access object.
        market_dao (MarketDAO): market table data access object.
        wd_dao (WorldDemandDAO): world_demand table DAO.

    Returns:
        list[Supply]: current supplies for all users.
    """
    ts = datetime.now()
    cycle = await cycle_dao.get_current()
    supplies = await dao.select(cycle=cycle.id)
    velocities = await get_supply_velocities(market_dao=market_dao, wd_dao=wd_dao, cycle=cycle.id, tau_s=cycle.tau_s)
    for supply in supplies:
        if supply.delivered == 0:
            supply.delivered = delivered_items(
                ts_start=supply.ts_start,
                ts_finish=ts,
                velocity=velocities[supply.market],
                quantity=supply.quantity,
            )
    return supplies


@router.post("/new")
async def make_supply(  # noqa: WPS217
    bid: SupplyBid,
    user: User = Depends(get_current_user),
    dao: SupplyDAO = Depends(),
    cycle_dao: CycleDAO = Depends(),
    transaction_dao: TransactionDAO = Depends(),
    wh_dao: WarehouseDAO = Depends(),
    bulletin_dao: BulletinDAO = Depends(),
    market_dao: MarketDAO = Depends(),
    user_dao: UserDAO = Depends(),
) -> None:
    """Make supply route.

    Args:
        bid (SupplyBid): supply bid.
        user (User): auth user.
        dao (SupplyDAO): supplies table data access object.
        cycle_dao (CycleDAO): cycle table data access object.
        transaction_dao (TransactionDAO): transactions table DAO.
        wh_dao (WarehouseDAO): warehouses table DAO.
        bulletin_dao (BulletinDAO): bulletins table DAO.
        market_dao (MarketDAO): markets table DAO.
        user_dao (UserDAO): users table DAO.

    Raises:
        HTTPException: quantity <= 0.
        HTTPException: warehouse < quantity.
    """
    if bid.quantity <= 0:
        raise HTTPException(status_code=400, detail=f"Incorrect {bid.quantity = }")
    cycle = await cycle_dao.get_current()
    market_names = await get_market_names(market_dao)
    user_names = await user_dao.get_names()
    if not await check_storage(cycle=cycle.id, user=user.id, market=bid.market, quantity=bid.quantity, wh_dao=wh_dao):
        raise HTTPException(status_code=400, detail="Not enough items in warehouse for supply")
    await transaction_dao.create(
        cycle=cycle.id,
        user=user.id,
        amount=-cycle.beta,
        description="Fee for market operations (supply)",
    )
    await dao.create(cycle=cycle.id, user=user.id, market=bid.market, quantity=bid.quantity)
    await bulletin_dao.create(
        cycle=cycle.id,
        user=user_names[user.id],
        market=market_names[bid.market],
        quantity=bulletin_quantity(bid.quantity),
    )
