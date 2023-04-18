from datetime import datetime

from fastapi import Depends
from sqlmodel import Field, SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from egame179_backend.db import get_db_session


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

    async def get_user_supplies(self, user_id: int, cycle: int) -> list[Supply]:
        """Get all supplies for particular user.

        Args:
            user_id (int): target user id.
            cycle (int): target cycle.

        Returns:
            list[Supply]: user supplies.
        """
        query = select(Supply).where(Supply.user_id == user_id, Supply.cycle == cycle)
        query = query.order_by(Supply.ts_start)
        raw_supplies = await self.session.exec(query)  # type: ignore
        return raw_supplies.all()

    async def get_supplies(self, cycle: int) -> list[Supply]:
        """Get all supplies for all users.

        Args:
            cycle (int): target cycle.

        Returns:
            list[Supply]: supplies.
        """
        query = select(Supply).where(Supply.cycle == cycle).order_by(Supply.ts_start)
        raw_supplies = await self.session.exec(query)  # type: ignore
        return raw_supplies.all()

    async def create_supply(self, cycle: int, user_id: int, market_id: int, declared_amount: int) -> None:
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

    async def finish_supply(self, supply: Supply) -> None:
        """Finish ongoing supply.

        Args:
            supply (Supply): target Supply object.
        """
        supply.ts_finish = datetime.now()
        self.session.add(supply)
        await self.session.commit()
