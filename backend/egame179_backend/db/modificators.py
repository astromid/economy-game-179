from fastapi import Depends
from sqlmodel import Field, SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from egame179_backend.db.session import get_db_session


class FeeModificator(SQLModel, table=True):
    """Modificators table."""

    __tablename__ = "fee_modificators"  # type: ignore

    cycle: int = Field(primary_key=True)
    user: int = Field(primary_key=True)
    fee: str = Field(primary_key=True)
    coeff: float


class FeeModificatorDAO:
    """Class for accessing fee modificators table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def select(self, cycle: int, user: int | None = None, fee: str | None = None) -> list[FeeModificator]:
        """Get cycle modificators.

        Args:
            cycle (int): target cycle.
            user (int, optional): target user id. If None, all modificators return.
            fee (str, optional): target fee name. If None, all modificators return.

        Returns:
            list[Modificator]: cycle modificators.
        """
        query = select(FeeModificator).where(FeeModificator.cycle == cycle)
        if user is not None:
            query = query.where(FeeModificator.user == user)
        if fee is not None:
            query = query.where(FeeModificator.fee == fee)
        raw_modificators = await self.session.exec(query)  # type: ignore
        return raw_modificators.all()

    async def create(self, cycle: int, user: int, fee: str, coeff: float) -> None:
        """Create new cycle modificator.

        Args:
            cycle (int): modificator cycle.
            user (int): modificator user id.
            fee (str): modified fee name.
            coeff (float): modificator value.
        """
        self.session.add(FeeModificator(cycle=cycle, user=user, fee=fee, coeff=coeff))
        await self.session.commit()
