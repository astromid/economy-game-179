from fastapi import APIRouter, Depends, HTTPException, Security
from pydantic import BaseModel

from egame179_backend.api.auth.dependencies import get_current_user
from egame179_backend.db import BalanceDAO, CycleDAO, MarketDAO, MarketPriceDAO, ThetaDAO, TransactionDAO
from egame179_backend.db.production import Production, ProductionDAO
from egame179_backend.db.user import User
from egame179_backend.engine.math import production_cost
from egame179_backend.engine.utility import check_balance, get_market_names

router = APIRouter()


class ProductionBid(BaseModel):
    """Production bid model."""

    market: int
    quantity: int


@router.get("/list/user")
async def get_user_production(
    user: User = Depends(get_current_user),
    dao: ProductionDAO = Depends(),
) -> list[Production]:
    """Get production history for user.

    Args:
        user (User): authenticated user data.
        dao (ProductionDAO): production table data access object.

    Returns:
        list[Production]: production history for user.
    """
    return await dao.select(user.id)


@router.get("/list/all", dependencies=[Security(get_current_user, scopes=["root"])])
async def get_production(dao: ProductionDAO = Depends()) -> list[Production]:
    """Get production history for all users.

    Args:
        dao (ProductionDAO): production table data access object.

    Returns:
        list[Production]: production history for all users.
    """
    return await dao.select()


@router.post("/new")
async def new_production(  # noqa: WPS217
    bid: ProductionBid,
    user: User = Depends(get_current_user),
    dao: ProductionDAO = Depends(),
    cycle_dao: CycleDAO = Depends(),
    market_dao: MarketDAO = Depends(),
    price_dao: MarketPriceDAO = Depends(),
    balance_dao: BalanceDAO = Depends(),
    theta_dao: ThetaDAO = Depends(),
    transaction_dao: TransactionDAO = Depends(),
) -> None:
    """Buy products route.

    Args:
        bid (ProductionBid): buy bid.
        user (User): auth user.
        dao (ProductionDAO): production table data access object.
        cycle_dao (CycleDAO): cycle table data access object.
        market_dao (MarketDAO): markets table DAO.
        price_dao (MarketPriceDAO): market prices table DAO.
        balance_dao (BalanceDAO): balances table DAO.
        theta_dao (ThetaDAO): thetas table DAO.
        transaction_dao (TransactionDAO): transactions table DAO.

    Raises:
        HTTPException: quantity <= 0.
        HTTPException: insufficient balance for transaction.
    """
    if bid.quantity <= 0:
        raise HTTPException(status_code=400, detail=f"Incorrect {bid.quantity = }")
    cycle = await cycle_dao.get_current()
    market_names = await get_market_names(market_dao)
    price = await price_dao.get(cycle=cycle.id, market=bid.market)
    theta = await theta_dao.get(user=user.id, cycle=cycle.id, market=bid.market)
    cost = production_cost(theta=theta, price=price.buy, quantity=bid.quantity)
    if not await check_balance(cycle=cycle.id, user=user.id, amount=cost, balance_dao=balance_dao):
        raise HTTPException(status_code=400, detail="Not enough money for production")
    await transaction_dao.create(
        cycle=cycle.id,
        user=user.id,
        amount=-cost,
        description=f"Production cost of {bid.quantity} items of {market_names[bid.market]}",
    )
    await dao.create(cycle=cycle.id, user=user.id, market=bid.market, quantity=bid.quantity)
