from datetime import datetime

from fastapi import Depends
from sqlmodel import Field, SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from egame179_backend.db import get_db_session


class Transaction(SQLModel, table=True):
    """Transactions table."""

    __tablename__ = "transactions"  # type: ignore

    id: int = Field(default=None, primary_key=True)
    ts: datetime
    cycle: int
    user_id: int
    amount: float
    description: str


class TransactionDAO:
    """Class for accessing transactions table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def get(self, user_id: int | None) -> list[Transaction]:
        """Get game transactions.

        Args:
            user_id (int, optional): target user id. If None, all transactions return.

        Returns:
            list[Transaction]: game transactions.
        """
        query = select(Transaction).order_by(Transaction.ts)
        if user_id is not None:
            query = query.where(Transaction.user_id == user_id)
        raw_transactions = await self.session.exec(query)  # type: ignore
        return raw_transactions.all()

    async def create(self, cycle: int, user_id: int, amount: float, description: str) -> None:
        """Create new transaction.

        Args:
            cycle (int): transaction cycle.
            user_id (int): target user id.
            amount (float): amout of money.
            description (str): description.
        """
        self.session.add(Transaction(
            ts=datetime.now(),
            cycle=cycle,
            user_id=user_id,
            amount=amount,
            description=description,
        ))
        await self.session.commit()
