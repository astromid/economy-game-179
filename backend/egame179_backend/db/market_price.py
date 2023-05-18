from fastapi import Depends
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from egame179_backend.db.session import get_db_session


class MarketPrice(SQLModel, table=True):
    """Market prices table."""

    __tablename__ = "market_prices"  # type: ignore

    cycle: int
    market: int
    buy: float
    sell: float


class MarketPriceDAO:
    """Class for accessing market prices table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def get(self, cycle: int, market: int) -> MarketPrice:
        """Get buy & sell prices for target market on target cycle.

        Args:
            cycle (int): target cycle.
            market (int): target market id.

        Returns:
            MarketPrice: target price record.
        """
        query = select(MarketPrice).where(MarketPrice.cycle == cycle, MarketPrice.market == market)
        raw_price = await self.session.exec(query)  # type: ignore
        return raw_price.one()

    async def select(self, cycle: int | None = None) -> list[MarketPrice]:
        """Get prices for all markets.

        Args:
            cycle (int, optional): target cycle. If None, prices for all cycles return.

        Returns:
            list[Price]: market prices.
        """
        query = select(MarketPrice).order_by(MarketPrice.cycle)
        if cycle is not None:
            query = query.where(MarketPrice.cycle == cycle)
        raw_prices = await self.session.exec(query)  # type: ignore
        return raw_prices.all()

    async def create(self, cycle: int, new_prices: dict[int, tuple[float, float]]) -> None:
        """Create market prices for new cycle.

        Args:
            cycle (int): target cycle.
            new_prices (dict[int, tuple[float, float]]): {market id: (buy price, sell price)}
        """
        prices = [
            MarketPrice(cycle=cycle, market=market, buy=buy, sell=sell)
            for market, (buy, sell) in new_prices.items()
        ]
        self.session.add_all(prices)
        await self.session.commit()
