from fastapi import Depends
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from egame179_backend.db.session import get_db_session


class SyncStatus(SQLModel, table=True):
    """Sync status table."""

    __tablename__ = "sync_status"  # type: ignore

    user: int
    synced: bool


class SyncStatusDAO:
    """Class for accessing sync status table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def select(self) -> list[SyncStatus]:
        """Get all players status.

        Returns:
            list[SyncStatus]: players sync statuses.
        """
        query = select(SyncStatus)
        raw_statuses = await self.session.exec(query)  # type: ignore
        return raw_statuses.all()

    async def sync(self, user: int) -> None:
        """Change user status to synced.

        Args:
            user (int): target user id.
        """
        query = select(SyncStatus).where(SyncStatus.user == user)
        raw_status = await self.session.exec(query)  # type: ignore
        status = raw_status.one()
        status.synced = True
        self.session.add(status)
        await self.session.commit()

    async def desync_all(self) -> None:
        """Change all player statuses to desync."""
        statuses = await self.select()
        for status in statuses:
            status.synced = False
        self.session.add_all(statuses)
        await self.session.commit()
