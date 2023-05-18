import itertools
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
    quantity: int


class ProductionDAO:
    """Class for accessing production table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def select(self, cycle: int | None = None, user: int | None = None) -> list[Production]:
        """Get production log.

        Args:
            cycle (int, optional): production cycle. If None, all log records return.
            user (int, optional): target user id. If None, all log records return.

        Returns:
            list[Production]: production log (excluding axuiliary zeros).
        """
        query = select(Production).where(Production.quantity > 0).order_by(Production.id)
        if cycle is not None:
            query = query.where(Production.cycle == cycle)
        if user is not None:
            query = query.where(Production.user == user)
        raw_production = await self.session.exec(query)  # type: ignore
        return raw_production.all()

    async def create(self, cycle: int, user: int, market: int, quantity: int) -> None:
        """Create new production log record.

        Args:
            cycle (int): production cycle.
            user (int): target user id.
            market (int): production market id.
            quantity (int): number of items.
        """
        self.session.add(Production(ts=datetime.now(), cycle=cycle, user=user, market=market, quantity=quantity))
        await self.session.commit()

    async def create_auxiliary(self, cycle: int, users: list[int], markets: list[int]) -> None:
        """Create auxiliary production log records.

        Args:
            cycle (int): production cycle.
            users (list[int]): list of user ids.
            markets (list[int]): list of market ids.
        """
        auxilary_production = [
            Production(ts=datetime.now(), cycle=cycle, user=user, market=market, quantity=0)
            for user, market in itertools.product(users, markets)
        ]
        self.session.add_all(auxilary_production)
        await self.session.commit()
