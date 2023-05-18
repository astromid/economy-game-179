from fastapi import Depends
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from egame179_backend.db.session import get_db_session


class Stock(SQLModel, table=True):
    """Stocks table."""

    __tablename__ = "stocks"  # type: ignore

    cycle: int
    user: int
    price: float


class StockDAO:
    """Class for accessing stocks table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def select(self, cycle: int | None = None) -> list[Stock]:
        """Get stock prices history for all players & NPCs.

        Args:
            cycle (int, optional): target cycle. Defaults to None.

        Returns:
            list[Stock]: stocks history.
        """
        query = select(Stock)
        if cycle is not None:
            query = query.where(Stock.cycle == cycle)
        raw_stocks = await self.session.exec(query)  # type: ignore
        return raw_stocks.all()

    async def create(self, cycle: int, new_stocks: dict[int, float]) -> None:
        """Create stock prices for new cycle.

        Args:
            cycle (int): target cycle.
            new_stocks (dict[int, float]): {user: price}.
        """
        stocks = [Stock(cycle=cycle, user=user, price=price) for user, price in new_stocks.items()]
        self.session.add_all(stocks)
        await self.session.commit()
