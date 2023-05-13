import math
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
    user_id: int
    market_id: int
    declared_amount: int
    amount: int = 0


class SupplyDAO:
    """Class for accessing supplies table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def get(self, cycle: int, user_id: int | None = None) -> list[Supply]:
        """Get all supplies for particular user.

        Args:
            cycle (int): target cycle.
            user_id (int, optional): target user id. If None, all user records return.

        Returns:
            list[Supply]: user supplies.
        """
        query = select(Supply).where(Supply.cycle == cycle).order_by(Supply.ts_start)
        if user_id is not None:
            query = query.where(Supply.user_id == user_id)
        raw_supplies = await self.session.exec(query)  # type: ignore
        return raw_supplies.all()

    async def create(self, cycle: int, user_id: int, market_id: int, declared_amount: int) -> None:
        """Create new supply.

        Args:
            cycle (int): cycle.
            user_id (int): target user id.
            market_id (int): target market id.
            declared_amount (int): number of items in supply.
        """
        self.session.add(
            Supply(
                ts_start=datetime.now(),
                cycle=cycle,
                user_id=user_id,
                market_id=market_id,
                declared_amount=declared_amount,
            ),
        )
        await self.session.commit()

    async def finish_ongoing(self, ts_finish: datetime, velocities: dict[int, float]) -> None:
        """Finish all ongoing supplies and update real delivered amount.

        Args:
            ts_finish (datetime): cycle finish time.
            velocities (dict[int, float]): supply velocity (items per sec) for each market.
        """
        query = select(Supply).where(Supply.amount == 0)
        raw_supplies = await self.session.exec(query)  # type: ignore
        for supply in raw_supplies.all():
            delivery_time = (ts_finish - supply.ts_start).total_seconds()
            max_delivered_amount = math.floor(velocities[supply.market_id] * delivery_time)
            supply.amount = min(supply.declared_amount, max_delivered_amount)
            supply.ts_finish = ts_finish
            await self.add(supply)

    async def add(self, supply: Supply) -> None:
        """Create or update supply.

        Args:
            supply (Supply): target supply record.
        """
        self.session.add(supply)
        await self.session.commit()
