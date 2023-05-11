from fastapi import Depends
from sqlmodel import Field, SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from egame179_backend.db.session import get_db_session


class Market(SQLModel, table=True):
    """Markets table."""

    __tablename__ = "markets"  # type: ignore

    id: int = Field(primary_key=True)
    name: str
    ring: int
    link1: int
    link2: int
    link3: int
    link4: int | None
    link5: int | None


class UnlockedMarket(SQLModel, table=True):
    """Unlocked markets table."""

    __tablename__ = "unlocked_markets"  # type: ignore

    user_id: int = Field(primary_key=True)
    market_id: int = Field(primary_key=True)
    protected: bool


class MarketDAO:
    """Class for accessing markets table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def get_all(self) -> list[Market]:
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

    async def get_all(self, user_id: int | None = None) -> list[UnlockedMarket]:
        """Get unlocked markets for paticular user.

        Args:
            user_id (int, optional): user id. If None, markets for all users return.

        Returns:
            list[UnlockedMarket]: unlocked markets.
        """
        query = select(UnlockedMarket).order_by(UnlockedMarket.protected)
        if user_id is not None:
            query = query.where(UnlockedMarket.user_id == user_id)
        raw_markets = await self.session.exec(query)  # type: ignore
        return raw_markets.all()

    async def unlock(self, user_id: int, market_id: int) -> None:
        """Unlock particular market for particular user.

        Args:
            user_id (int): target user id.
            market_id (int): target market id.
        """
        self.session.add(UnlockedMarket(user_id=user_id, market_id=market_id, protected=False))
        await self.session.commit()

    async def lock(self, user_id: int, market_id: int) -> None:
        """Remove unlock record about particular market for particular user.

        Args:
            user_id (int): target user id.
            market_id (int): target market id.
        """
        query = select(UnlockedMarket).where(
            UnlockedMarket.user_id == user_id,
            UnlockedMarket.market_id == market_id,
            not UnlockedMarket.protected,
        )
        raw_record = await self.session.exec(query)  # type: ignore
        record = raw_record.one_or_none()
        if record is not None:
            await self.session.delete(record)
            await self.session.commit()
