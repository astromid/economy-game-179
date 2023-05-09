"""Communication with database module."""
from collections.abc import AsyncGenerator

from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.requests import Request

from egame179_backend.db.balance import BalanceDAO
from egame179_backend.db.cycle import CycleDAO
from egame179_backend.db.cycle_params import CycleParamsDAO
from egame179_backend.db.market import MarketDAO, UnlockedMarketDAO
from egame179_backend.db.price import PriceDAO
from egame179_backend.db.product import ProductDAO
from egame179_backend.db.supply import SupplyDAO
from egame179_backend.db.transaction import TransactionDAO
from egame179_backend.db.user import UserDAO


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """Create and get database session.

    Args:
        request (Request): current request.

    Yields:
        AsyncSession: database session.
    """
    session: AsyncSession = request.app.state.db_session_factory()
    async with session:
        yield session

__all__ = [
    "BalanceDAO",
    "CycleDAO",
    "CycleParamsDAO",
    "MarketDAO",
    "UnlockedMarketDAO",
    "PriceDAO",
    "ProductDAO",
    "SupplyDAO",
    "TransactionDAO",
    "UserDAO",
    "get_db_session",
]
