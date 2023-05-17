from datetime import datetime

from fastapi import Depends
from sqlmodel import Field, SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from egame179_backend.db.session import get_db_session


class Supply(SQLModel, table=True):
    """Supplies table."""

    __tablename__ = "supplies"  # type: ignore

    id: int = Field(default=None, primary_key=True)
    ts_start: datetime
    ts_finish: datetime | None = None
    cycle: int
    user: int
    market: int
    quantity: int
    delivered: int = 0


class SupplyDAO:
    """Class for accessing supplies table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def select(self, cycle: int, user: int | None = None, ongoing=False) -> list[Supply]:
        """Get all supplies on a target cycle.

        Args:
            cycle (int): target cycle.
            user (int, optional): target user id. If None, all user records return.
            ongoing (bool, optional): if True, only ongoing supplies return.

        Returns:
            list[Supply]: supplies.
        """
        query = select(Supply).where(Supply.cycle == cycle).order_by(Supply.id)
        if user is not None:
            query = query.where(Supply.user == user)
        if ongoing:
            query = query.where(Supply.delivered == 0)
        raw_supplies = await self.session.exec(query)  # type: ignore
        return raw_supplies.all()

    async def create(self, cycle: int, user: int, market: int, quantity: int) -> None:
        """Create new supply.

        Args:
            cycle (int): target cycle.
            user (int): target user id.
            market (int): target market id.
            quantity (int): number of items in supply.
        """
        self.session.add(Supply(ts_start=datetime.now(), cycle=cycle, user=user, market=market, quantity=quantity))
        await self.session.commit()

    async def update(self, supplies: list[Supply]) -> None:
        """Update supplies.

        Args:
            supplies (list[Supply]): supplies to update.
        """
        self.session.add_all(supplies)
        await self.session.commit()
