from datetime import datetime

from fastapi import Depends
from sqlmodel import Field, SQLModel, col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from egame179_backend.db import get_db_session


class Cycle(SQLModel, table=True):
    """Cycles table."""

    __tablename__ = "cycles"  # type: ignore

    cycle: int | None = Field(default=None, primary_key=True)
    ts_start: datetime | None = None
    ts_finish: datetime | None = None


class CycleDAO:
    """Class for accessing cycles table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def get_cycle(self) -> Cycle:
        """Get current cycle.

        Returns:
            Cycle: current cycle info.
        """
        query = select(Cycle).order_by(col(Cycle.cycle).desc()).limit(1)
        raw_cycle = await self.session.exec(query)  # type: ignore
        return raw_cycle.one()

    async def create_cycle(self) -> None:
        """Create new cycle."""
        self.session.add(Cycle())
        await self.session.commit()

    async def start_cycle(self) -> None:
        """Start current cycle."""
        cycle = await self.get_cycle()
        cycle.ts_start = datetime.now()
        self.session.add(cycle)
        await self.session.commit()

    async def finish_cycle(self) -> None:
        """Finish current cycle."""
        cycle = await self.get_cycle()
        cycle.ts_finish = datetime.now()
        self.session.add(cycle)
        await self.session.commit()
