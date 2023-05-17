from datetime import datetime

from fastapi import Depends
from sqlmodel import Field, SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from egame179_backend.db.session import get_db_session


class Transaction(SQLModel, table=True):
    """Transactions table."""

    __tablename__ = "transactions"  # type: ignore

    id: int = Field(default=None, primary_key=True)
    ts: datetime
    cycle: int
    user: int
    amount: float
    description: str


class TransactionDAO:
    """Class for accessing transactions table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def select(self, user: int | None = None) -> list[Transaction]:
        """Get game transactions.

        Args:
            user (int, optional): target user id. If None, all transactions return.

        Returns:
            list[Transaction]: game transactions.
        """
        query = select(Transaction).order_by(Transaction.id)
        if user is not None:
            query = query.where(Transaction.user == user)
        raw_transactions = await self.session.exec(query)  # type: ignore
        return raw_transactions.all()

    async def create(self, cycle: int, user: int, amount: float, description: str) -> None:
        """Create new transaction.

        Args:
            cycle (int): transaction cycle.
            user (int): transaction user id.
            amount (float): amout of money.
            description (str): trasnaction description.
        """
        self.session.add(Transaction(ts=datetime.now(), cycle=cycle, user=user, amount=amount, description=description))
        await self.session.commit()

    async def add(self, transactions: list[Transaction]) -> None:
        """Add transactions.

        Args:
            transactions (list[Transaction]): transactions to update.
        """
        self.session.add_all(transactions)
        await self.session.commit()
