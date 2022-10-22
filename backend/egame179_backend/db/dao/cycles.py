from datetime import datetime

from fastapi import Depends
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from egame179_backend.db.dependencies import get_db_session
from egame179_backend.db.models import Cycle


class CycleDAO:
    """Class for accessing cycles table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def get_current_cycle(self) -> Cycle:
        """Get current (unfinished) cycle.

        Returns:
            Cycle: current cycle info.
        """
        query = select(Cycle).order_by(col(Cycle.cycle).desc()).limit(1)
        raw_cycle = await self.session.exec(query)  # type: ignore
        return raw_cycle.one()

    async def finish_current_cycle(self) -> Cycle:
        """Finish current cycle.

        Returns:
            Cycle: finished cycle info.
        """
        current_cycle = await self.get_current_cycle()
        current_cycle.finished = datetime.now()
        self.session.add(current_cycle)
        await self.session.commit()
        return current_cycle

    async def start_new_cycle(self) -> None:
        """Start new cycle."""
        self.session.add(Cycle())
        await self.session.commit()
