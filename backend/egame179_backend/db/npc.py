from fastapi import Depends
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from egame179_backend.db.session import get_db_session


class Npc(SQLModel, table=True):
    """NPCs table."""

    __tablename__ = "npcs"  # type: ignore

    user: int
    ring: int


class NpcDAO:
    """Class for accessing NPCs table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def select(self) -> list[Npc]:
        """Get NPCs info.

        Returns:
            list[Npc]: NPCs info.
        """
        query = select(Npc)
        raw_npcs = await self.session.exec(query)  # type: ignore
        return raw_npcs.all()
