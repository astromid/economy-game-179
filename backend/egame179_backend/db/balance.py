from fastapi import Depends
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from egame179_backend.db.session import get_db_session


class Balance(SQLModel, table=True):
    """Balances table."""

    __tablename__ = "balances"  # type: ignore

    cycle: int
    user: int
    balance: float


class BalanceDAO:
    """Class for accessing balances table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def get(self, cycle: int, user: int) -> float:
        """Get user balance on particular cycle.

        Args:
            cycle (int): target cycle.
            user (int): target user id.

        Returns:
            float: target balance.
        """
        query = select(Balance).where(Balance.cycle == cycle, Balance.user == user)
        raw_balance = await self.session.exec(query)  # type: ignore
        return raw_balance.one().balance

    async def select(self, cycle: int | None = None, user: int | None = None, overdrafted=False) -> list[Balance]:
        """Get user balances.

        Args:
            cycle (int): target cycle. If None, all cycles return.
            user (int, optional): target user id. If None, all user balances return.
            overdrafted (bool, optional): if True, only overdrafted balances return.

        Returns:
            list[Balance]: users balances.
        """
        query = select(Balance)
        if cycle is not None:
            query = query.where(Balance.cycle == cycle)
        if user is not None:
            query = query.where(Balance.user == user)
        if overdrafted:
            query = query.where(Balance.balance < 0)
        raw_balances = await self.session.exec(query)  # type: ignore
        return raw_balances.all()
