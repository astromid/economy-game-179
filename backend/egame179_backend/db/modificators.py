from fastapi import Depends
from sqlmodel import Field, SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from egame179_backend.db.session import get_db_session


class Modificator(SQLModel, table=True):
    """Modificators table."""

    __tablename__ = "modificators"  # type: ignore

    cycle: int = Field(primary_key=True)
    user: int = Field(primary_key=True)
    market: int = Field(primary_key=True)
    parameter: str = Field(primary_key=True)
    value: float  # noqa: WPS110


class ModificatorDAO:
    """Class for accessing modificators table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def select(self, cycle: int, user: int | None = None) -> list[Modificator]:
        """Get cycle modificators.

        Args:
            cycle (int): target cycle.
            user (int, optional): target user id. If None, all transactions return.

        Returns:
            list[Modificator]: cycle modificators.
        """
        query = select(Modificator).where(Modificator.cycle == cycle)
        if user is not None:
            query = query.where(Modificator.user == user)
        raw_modificators = await self.session.exec(query)  # type: ignore
        return raw_modificators.all()

    async def create(self, cycle: int, user: int, market: int, parameter: str, value: float) -> None:  # noqa: WPS110
        """Create new cycle modificator.

        Args:
            cycle (int): modificator cycle.
            user (int): modificator user id.
            market (int): modificator market id.
            parameter (str): modificator parameter.
            value (float): modificator value.
        """
        self.session.add(Modificator(cycle=cycle, user=user, market=market, parameter=parameter, value=value))
        await self.session.commit()
