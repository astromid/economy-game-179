from datetime import datetime

from fastapi import Depends
from sqlmodel import Field, SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from egame179_backend.db.session import get_db_session


class Bulletin(SQLModel, table=True):
    """Bulletins table."""

    __tablename__ = "bulletins"  # type: ignore

    id: int = Field(default=None, primary_key=True)
    ts: datetime
    cycle: int
    user: int
    market: int
    text: str


class BulletinDAO:
    """Class for accessing bulletins table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def select(self, cycle: int) -> list[Bulletin]:
        """Get information bulletins for cycle.

        Args:
            cycle (int): target cycle.

        Returns:
            list[Bulletin]: supply information bulletins.
        """
        query = select(Bulletin).where(Bulletin.cycle == cycle).order_by(Bulletin.id)
        raw_bulletins = await self.session.exec(query)  # type: ignore
        return raw_bulletins.all()

    async def create(self, cycle: int, user: int, market: int, text: str) -> None:
        """Create new information bulletin.

        Args:
            cycle (int): bulletin cycle.
            user (int): bulletin user id.
            market (int): bulletin market id.
            text (str): bulletin text.
        """
        self.session.add(Bulletin(ts=datetime.now(), cycle=cycle, user=user, market=market, text=text))
        await self.session.commit()
