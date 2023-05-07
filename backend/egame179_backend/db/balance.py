from fastapi import Depends
from sqlmodel import Field, SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from egame179_backend.db import get_db_session


class Balance(SQLModel, table=True):
    """Balances table."""

    __tablename__ = "balances"  # type: ignore

    cycle: int = Field(primary_key=True)
    user_id: int = Field(primary_key=True)
    amount: float


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

    async def get_balances(self) -> list[Balance]:
        """Get all balances.

        Returns:
            list[Balance]: all balances.
        """
        query = select(Balance).order_by(Balance.cycle)
        raw_balances = await self.session.exec(query)  # type: ignore
        return raw_balances.all()

    async def update_balance(self, cycle: int, user_id: int, amount: float) -> None:
        """Update user balance.

        Args:
            cycle (int): target cycle.
            user_id (int): target user.
            amount (float): new amout of money.
        """
        query = select(Balance).where(Balance.cycle == cycle, Balance.user_id == user_id)
        raw_balance = await self.session.exec(query)  # type: ignore
        balance = raw_balance.one()
        balance.amount = amount
        self.session.add(balance)
        await self.session.commit()
