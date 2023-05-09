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

    async def get(self, user_id: int | None = None) -> list[Balance]:
        """Get user balances.

        Args:
            user_id (int, optional): target user id. If None, all user balances return.

        Returns:
            list[Balance]: users balances.
        """
        query = select(Balance).order_by(Balance.cycle)
        if user_id is not None:
            query = query.where(Balance.user_id == user_id)
        raw_balances = await self.session.exec(query)  # type: ignore
        return raw_balances.all()

    async def get_on_cycle(self, cycle: int, user_id: int) -> Balance:
        """Get user balance on particular cycle.

        Args:
            cycle (int): target cycle.
            user_id (int): target user id.

        Returns:
            Balance: target balance.
        """
        query = select(Balance).where(Balance.user_id == user_id, Balance.cycle == cycle)
        raw_balance = await self.session.exec(query)  # type: ignore
        return raw_balance.one()

    async def get_overdrafted(self, cycle: int) -> list[Balance]:
        """Get overdrafted balances.

        Args:
            cycle (int): target cycle.

        Returns:
            list[Balance]: overdrafted balances.
        """
        query = select(Balance).where(Balance.cycle == cycle, Balance.amount < 0)
        raw_balances = await self.session.exec(query)  # type: ignore
        return raw_balances.all()

    async def create(self, cycle: int, user_id: int, amount: float) -> None:
        """Creane new balance record.

        Args:
            cycle (int): target cycle.
            user_id (int): target user.
            amount (float): amount of money.
        """
        self.session.add(Balance(cycle=cycle, user_id=user_id, amount=amount))
        await self.session.commit()

    async def update(self, cycle: int, user_id: int, delta: float) -> None:
        """Update user balance.

        Args:
            cycle (int): target cycle.
            user_id (int): target user.
            delta (float): delta amount of money (add up to current balance).
        """
        query = select(Balance).where(Balance.cycle == cycle, Balance.user_id == user_id)
        raw_balance = await self.session.exec(query)  # type: ignore
        balance = raw_balance.one()
        balance.amount += delta
        self.session.add(balance)
        await self.session.commit()
