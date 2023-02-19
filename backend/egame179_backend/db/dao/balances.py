from fastapi import Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from egame179_backend.db.dependencies import get_db_session
from egame179_backend.db.models import Balance


class BalanceDAO:
    """Class for accessing balances table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def get_user_balances(self, user_id: int) -> list[Balance]:
        """Get user balances.

        Args:
            user_id (int): user id.

        Returns:
            list[Balance]: user balances.
        """
        query = select(Balance).where(Balance.user_id == user_id).order_by(Balance.cycle)
        raw_balances = await self.session.exec(query)  # type: ignore
        return raw_balances.all()

    async def get_all_balances(self) -> list[Balance]:
        """Get all balances.

        Returns:
            list[Balance]: all balances.
        """
        query = select(Balance).order_by(Balance.cycle)
        raw_balances = await self.session.exec(query)  # type: ignore
        return raw_balances.all()
