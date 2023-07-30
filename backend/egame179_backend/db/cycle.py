from datetime import datetime

from fastapi import Depends
from sqlmodel import Field, SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from egame179_backend.db.session import get_db_session


class Cycle(SQLModel, table=True):
    """Cycles table."""

    __tablename__ = "cycles"  # type: ignore

    id: int = Field(primary_key=True)
    ts_start: datetime | None = None
    ts_finish: datetime | None = None
    alpha: float
    beta: float
    gamma: float
    tau_s: int
    coeff_h: int
    coeff_k: int
    coeff_l: int
    overdraft_rate: float


class CycleDAO:
    """Class for accessing cycles table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def get_current(self) -> Cycle:
        """Get current cycle.

        Returns:
            Cycle: current cycle info.
        """
        query = select(Cycle).where(Cycle.ts_finish == None)  # noqa: E711
        query = query.order_by(Cycle.id).limit(1)
        raw_cycle = await self.session.exec(query)  # type: ignore
        return raw_cycle.one()

    async def start(self) -> None:
        """Start current cycle."""
        cycle = await self.get_current()
        cycle.ts_start = datetime.now()
        self.session.add(cycle)
        await self.session.commit()

    async def finish(self) -> Cycle:
        """Finish current cycle.

        Returns:
            Cycle: finished cycle.
        """
        cycle = await self.get_current()
        cycle.ts_finish = datetime.now()
        self.session.add(cycle)
        await self.session.commit()
        return cycle
