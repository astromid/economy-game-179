from datetime import datetime

from fastapi import Depends
from sqlmodel import Field, SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from egame179_backend.db.session import get_db_session
from egame179_backend.engine.math import delivered_items


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

    async def select(self, cycle: int, user: int | None = None) -> list[Supply]:
        """Get all supplies on a target cycle.

        Args:
            cycle (int): target cycle.
            user (int, optional): target user id. If None, all user records return.

        Returns:
            list[Supply]: supplies.
        """
        query = select(Supply).where(Supply.cycle == cycle).order_by(Supply.id)
        if user is not None:
            query = query.where(Supply.user == user)
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

    async def finish(self, ts_finish: datetime, velocities: dict[int, float]) -> None:
        """Finish all ongoing supplies and update real delivered amount.

        Args:
            ts_finish (datetime): cycle finish time.
            velocities (dict[int, float]): supply velocity (items per sec) for each market.
        """
        query = select(Supply).where(Supply.delivered == 0)
        raw_supplies = await self.session.exec(query)  # type: ignore
        supplies: list[Supply] = raw_supplies.all()
        for supply in supplies:
            supply.delivered = delivered_items(
                ts_start=supply.ts_start,
                ts_finish=ts_finish,
                velocity=velocities[supply.market],
                quantity=supply.quantity,
            )
            supply.ts_finish = ts_finish
        self.session.add_all(supplies)
        await self.session.commit()
