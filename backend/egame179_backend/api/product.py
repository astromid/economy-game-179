from fastapi import APIRouter, Depends, Security
from pydantic import BaseModel

from egame179_backend import engine
from egame179_backend.api.auth.dependencies import get_current_user
from egame179_backend.db.balance import BalanceDAO
from egame179_backend.db.cycle import CycleDAO
from egame179_backend.db.market import MarketDAO, UnlockedMarketDAO
from egame179_backend.db.price import PriceDAO
from egame179_backend.db.product import Product, ProductDAO
from egame179_backend.db.transaction import TransactionDAO
from egame179_backend.db.user import User

router = APIRouter()


class MarketSharePlayer(BaseModel):
    """Market share with player visible info."""

    market_id: int
    user_id: int
    share: float | None = None
    position: int


class ProductionBid(BaseModel):
    """Production bid model."""

    market_id: int
    amount: int


@router.get("/user")
async def get_user_products(user: User = Depends(get_current_user), dao: ProductDAO = Depends()) -> list[Product]:
    """Get products history for user.

    Args:
        user (User): authenticated user data.
        dao (ProductDAO): products table data access object.

    Returns:
        list[Product]: products history for user.
    """
    return await dao.get(user.id)


@router.get("/all", dependencies=[Security(get_current_user, scopes=["root"])])
async def get_all_products(dao: ProductDAO = Depends()) -> list[Product]:
    """Get products history for all users.

    Args:
        dao (ProductDAO): products table data access object.

    Returns:
        list[Products]: products history for all users.
    """
    return await dao.get()


@router.get("/shares")
async def get_market_shares(  # noqa: WPS210
    user: User = Depends(get_current_user),
    dao: ProductDAO = Depends(),
    cycle_dao: CycleDAO = Depends(),
    market_dao: MarketDAO = Depends(),
    unlocked_market_dao: UnlockedMarketDAO = Depends(),
) -> list[MarketSharePlayer]:
    """Get player visible market shares.

    Args:
        user (User): authenticated user data.
        dao (ProductDAO): products table data access object.
        cycle_dao (CycleDAO): cycle table data access object.
        market_dao (MarketDAO): markets table data access object.
        unlocked_market_dao (UnlockedMarketDAO): unlocked markets table data access object.

    Returns:
        list[MarketSharePlayer]: market shares visible for player.
    """
    current_cycle = await cycle_dao.get_current()
    products = await dao.get()
    markets = await market_dao.get()
    unlocked_markets = await unlocked_market_dao.get(user.id)

    products = [product for product in products if (product.cycle == current_cycle.cycle and product.share > 0)]
    owned_markets = [umarket.market_id for umarket in unlocked_markets]
    shares = []
    for market in markets:
        market_products = sorted(
            [product for product in products if product.market_id == market.id],
            key=lambda product: product.share,
            reverse=True,
        )
        products_dict = {pos: prod.dict() for pos, prod in enumerate(market_products, start=1)}
        if market.id not in owned_markets:
            # filter information for non-owned markets
            products_dict = {pos: prod for pos, prod in products_dict.items() if pos <= 2}
            for prod in products_dict.values():
                prod["share"] = None
        shares.extend([
            MarketSharePlayer(
                market_id=market.id,
                user_id=product["user_id"],
                share=product["share"],
                position=pos,
            )
            for pos, product in products_dict.items()
        ])
    return shares


@router.post("/buy")
async def production(
    bid: ProductionBid,
    user: User = Depends(get_current_user),
    dao: ProductDAO = Depends(),
    cycle_dao: CycleDAO = Depends(),
    price_dao: PriceDAO = Depends(),
    balance_dao: BalanceDAO = Depends(),
    transaction_dao: TransactionDAO = Depends(),
) -> None:
    """Buy products route.

    Args:
        bid (ProductionBid): buy bid.
        user (User): auth user.
        dao (ProductDAO): products table data access object.
        cycle_dao (CycleDAO): cycle table data access object.
        price_dao (PriceDAO): prices table DAO.
        balance_dao (BalanceDAO): balances table DAO.
        transaction_dao (TransactionDAO): transactions table DAO.
    """
    current_cycle = await cycle_dao.get_current()
    buy_price, _ = await price_dao.get_market_price(market_id=bid.market_id, cycle=current_cycle.cycle)
    bid_price = bid.amount * buy_price
    transaction_success = await engine.make_transaction(
        cycle=current_cycle.cycle,
        user_id=user.id,
        amount=-bid_price,
        description=f"Buy {bid.amount} items (market_id = {bid.market_id})",
        overdraft=False,
        balance_dao=balance_dao,
        transaction_dao=transaction_dao,
    )
    if transaction_success:
        await dao.update_storage(cycle=current_cycle.cycle, user_id=user.id, market_id=bid.market_id, delta=bid.amount)
