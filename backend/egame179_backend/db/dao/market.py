from fastapi import Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from egame179_backend.db.dependencies import get_db_session
from egame179_backend.db.models import Market, UnlockedMarket


class MarketDAO:
    """Class for accessing markets table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def get_markets(self) -> list[Market]:
        """Get markets.

        Returns:
            list[Market]: markets in the game.
        """
        query = select(Market)
        raw_markets = await self.session.exec(query)  # type: ignore
        return raw_markets.all()


class UnlockedMarketDAO:
    """Class for accessing unlocked markets table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def get_user_unlocked_markets(self, user_id: int) -> list[UnlockedMarket]:
        """Get unlocked markets for paticular user.

        Args:
            user_id (int): user id.

        Returns:
            list[UnlockedMarket]: unlocked markets for the user.
        """
        query = select(UnlockedMarket).where(UnlockedMarket.user_id == user_id)
        raw_markets = await self.session.exec(query)  # type: ignore
        return raw_markets.all()

    async def get_all_unlocked_markets(self) -> list[UnlockedMarket]:
        """Get all unlocked markets.

        Returns:
            list[UnlockedMarket]: unlocked markets for all users.
        """
        query = select(UnlockedMarket)
        raw_markets = await self.session.exec(query)  # type: ignore
        return raw_markets.all()

    async def unlock_market_for_user(self, user_id: int, market_id: int) -> None:
        """Unlock particular market for particular user.

        Args:
            user_id (int): target user id
            market_id (int): target market id
        """
        self.session.add(UnlockedMarket(user_id=user_id, market_id=market_id, protected=False))
        await self.session.commit()

    async def lock_market_for_user(self, user_id: int, market_id: int) -> None:
        """Remove unlock record about particular market for particular user.

        Args:
            user_id (int): target user id
            market_id (int): target market id
        """
        query = select(UnlockedMarket).where(UnlockedMarket.user_id == user_id, UnlockedMarket.market_id == market_id)
        raw_record = await self.session.exec(query)  # type: ignore
        record = raw_record.one_or_none()
        if record is not None and not record.protected:
            await self.session.delete(record)
            await self.session.commit()
