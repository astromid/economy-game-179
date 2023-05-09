from fastapi import Depends
from sqlmodel import Field, SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from egame179_backend.db import get_db_session


class Price(SQLModel, table=True):
    """Transactions table."""

    __tablename__ = "prices"  # type: ignore

    cycle: int = Field(primary_key=True)
    market_id: int = Field(primary_key=True)
    buy: float
    sell: float


class PriceDAO:
    """Class for accessing prices table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def get(self, market_id: int, cycle: int) -> Price:
        """Get buy & sell prices for target market_id on target cycle.

        Args:
            market_id (int): target market id.
            cycle (int): target cycle.

        Returns:
            Price: target price record.
        """
        query = select(Price).where(Price.market_id == market_id, Price.cycle == cycle)
        raw_price = await self.session.exec(query)  # type: ignore
        return raw_price.one()

    async def get_all(self) -> list[Price]:
        """Get all prices for all markets.

        Returns:
            list[Price]: market prices.
        """
        query = select(Price).order_by(Price.cycle)
        raw_prices = await self.session.exec(query)  # type: ignore
        return raw_prices.all()

    async def create(self, cycle: int, market_id: int, buy: float, sell: float) -> None:
        """Create market price for new cycle.

        Args:
            cycle (int): cycle.
            market_id (int): target market id.
            buy (float): new buy price.
            sell (float): new sell price.
        """
        self.session.add(Price(cycle=cycle, market_id=market_id, buy=buy, sell=sell))
        await self.session.commit()
