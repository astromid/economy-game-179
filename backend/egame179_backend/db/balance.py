from fastapi import Depends
from sqlmodel import Field, SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from egame179_backend.db.session import get_db_session


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

    async def get(self, cycle: int, user_id: int) -> Balance:
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

    async def get_all(self, user_id: int | None = None, cycle: int | None = None) -> list[Balance]:
        """Get user balances.

        Args:
            user_id (int, optional): target user id. If None, all user balances return.

        Returns:
            list[Balance]: users balances.
        """
        query = select(Balance)
        if cycle is not None:
            query = query.where(Balance.cycle == cycle)
        if user_id is not None:
            query = query.where(Balance.user_id == user_id).order_by(Balance.cycle)
        raw_balances = await self.session.exec(query)  # type: ignore
        return raw_balances.all()

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

    async def add(self, balance: Balance) -> None:
        """Create or update balance.

        Args:
            balance (Balance): target balance record.
        """
        self.session.add(balance)
        await self.session.commit()
