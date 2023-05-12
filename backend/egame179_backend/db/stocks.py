from fastapi import Depends
from sqlmodel import Field, SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from egame179_backend.db.session import get_db_session

# TODO: refactor this to exculde hardcoded values
RING2NPC_ID = {0: 3, 1: 4, 2: 5}


class Stock(SQLModel, table=True):
    """Stocks table."""

    __tablename__ = "stocks"  # type: ignore

    cycle: int = Field(primary_key=True)
    user_id: int = Field(primary_key=True)
    price: float
    price_noise: float


class StockDAO:
    """Class for accessing stocks table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def get(self) -> list[Stock]:
        """Get stock prices history for all players & NPCs.

        Returns:
            list[Stock]: stocks history.
        """
        query = select(Stock)
        raw_stocks = await self.session.exec(query)  # type: ignore
        return raw_stocks.all()

    async def add(self, stock: Stock) -> None:
        """Create or update stock price.

        Args:
            stock (Stock): target stock record.
        """
        self.session.add(stock)
        await self.session.commit()
