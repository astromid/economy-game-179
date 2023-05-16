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

    async def get(self, user: int, cycle: int) -> Balance:
        """Get user balance on particular cycle.

        Args:
            user (int): target user id.
            cycle (int): target cycle.

        Returns:
            Balance: target balance.
        """
        query = select(Balance).where(Balance.user == user, Balance.cycle == cycle)
        raw_balance = await self.session.exec(query)  # type: ignore
        return raw_balance.one()

    async def select(self, user: int | None = None, cycle: int | None = None) -> list[Balance]:
        """Get user balances.

        Args:
            user (int, optional): target user id. If None, all user balances return.
            cycle (int): target cycle. If None, all cycles return.

        Returns:
            list[Balance]: users balances.
        """
        query = select(Balance).order_by(Balance.cycle)
        if user is not None:
            query = query.where(Balance.user == user)
        if cycle is not None:
            query = query.where(Balance.cycle == cycle)
        raw_balances = await self.session.exec(query)  # type: ignore
        return raw_balances.all()

    async def get_overdrafted(self, cycle: int) -> list[Balance]:
        """Get overdrafted balances on target cycle.

        Args:
            cycle (int): target cycle.

        Returns:
            list[Balance]: overdrafted balances.
        """
        query = select(Balance).where(Balance.cycle == cycle, Balance.balance < 0)
        raw_balances = await self.session.exec(query)  # type: ignore
        return raw_balances.all()
