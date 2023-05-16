from fastapi import Depends
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from egame179_backend.db.session import get_db_session


class Stock(SQLModel, table=True):
    """Stocks table."""

    __tablename__ = "stocks"  # type: ignore

    cycle: int
    user: int
    rel_income: float
    price: float


class StockDAO:
    """Class for accessing stocks table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def select(self) -> list[Stock]:
        """Get stock prices history for all players & NPCs.

        Returns:
            list[Stock]: stocks history.
        """
        query = select(Stock)
        raw_stocks = await self.session.exec(query)  # type: ignore
        return raw_stocks.all()

    async def create(self, cycle: int, new_stocks: dict[int, tuple[float, float]]) -> None:
        """Create stock prices for new cycle.

        Args:
            cycle (int): target cycle.
            new_stocks (dict[int, tuple[float, float]]): {user: (rel_income, price)}.
        """
        stocks = [
            Stock(cycle=cycle, user=user, rel_income=rel_income, price=price)
            for user, (rel_income, price) in new_stocks.items()
        ]
        self.session.add_all(stocks)
        await self.session.commit()
