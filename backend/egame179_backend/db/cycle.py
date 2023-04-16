from datetime import datetime

from fastapi import Depends
from sqlmodel import Field, SQLModel, col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from egame179_backend.db import get_db_session


class Cycle(SQLModel, table=True):
    """Cycles table."""

    __tablename__ = "cycles"  # type: ignore

    cycle: int | None = Field(default=None, primary_key=True)
    started: datetime | None = Field(default_factory=datetime.now)
    finished: datetime | None = None


class CycleDAO:
    """Class for accessing cycles table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def get_current_cycle(self) -> Cycle:
        """Get current cycle.

        Returns:
            Cycle: current cycle info.
        """
        query = select(Cycle).order_by(col(Cycle.cycle).desc()).limit(1)
        raw_cycle = await self.session.exec(query)  # type: ignore
        return raw_cycle.one()

    async def finish_current_cycle(self) -> None:
        """Finish current cycle."""
        current_cycle = await self.get_current_cycle()
        current_cycle.finished = datetime.now()
        self.session.add(current_cycle)
        await self.session.commit()

    async def start_new_cycle(self) -> None:
        """Start new cycle."""
        self.session.add(Cycle())
        await self.session.commit()
