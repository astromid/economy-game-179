from datetime import datetime

from fastapi import Depends
from sqlmodel import Field, SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from egame179_backend.db.session import get_db_session


class Production(SQLModel, table=True):
    """Production table."""

    __tablename__ = "production"  # type: ignore

    id: int = Field(default=None, primary_key=True)
    ts: datetime
    cycle: int
    user: int
    market: int
    amount: int


class ProductionDAO:
    """Class for accessing production table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def select(self, user: int | None) -> list[Production]:
        """Get production log.

        Args:
            user (int, optional): target user id. If None, all log records return.

        Returns:
            list[Production]: production log.
        """
        query = select(Production).order_by(Production.id)
        if user is not None:
            query = query.where(Production.user == user)
        raw_production = await self.session.exec(query)  # type: ignore
        return raw_production.all()

    async def create(self, cycle: int, user: int, market: int, amount: int) -> None:
        """Create new production log record.

        Args:
            cycle (int): production cycle.
            user (int): target user id.
            market (int): production market id.
            amount (int): number of items.
        """
        self.session.add(Production(ts=datetime.now(), cycle=cycle, user=user, market=market, amount=amount))
        await self.session.commit()
