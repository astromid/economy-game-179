from fastapi import Depends
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from egame179_backend.db.session import get_db_session


class Theta(SQLModel, table=True):
    """Thetas table."""

    __tablename__ = "thetas"  # type: ignore

    cycle: int
    user: int
    market: int
    theta: float


class ThetaDAO:
    """Class for accessing thetas table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def get(self, cycle: int, user: int, market: int) -> float:
        """Get production theta.

        Args:
            cycle (int): target cycle.
            user (int): target user id.
            market (int): target market.

        Returns:
            float: theta parameter.
        """
        query = select(Theta).where(Theta.cycle == cycle, Theta.user == user, Theta.market == market)
        raw_theta = await self.session.exec(query)  # type: ignore
        return raw_theta.one().theta

    async def select(self, cycle: int | None = None, user: int | None = None) -> list[Theta]:
        """Get all thetas.

        Args:
            cycle (int, optional): target cycle. If None, return thetas for all cycles.
            user (int, optional): target user id. If None, return thetas for all users.

        Returns:
            list[Theta]: theta records.
        """
        query = select(Theta)
        if cycle is not None:
            query = query.where(Theta.cycle == cycle)
        if user is not None:
            query = query.where(Theta.user == user).order_by(Theta.cycle)
        raw_thetas = await self.session.exec(query)  # type: ignore
        return raw_thetas.all()

    async def create(self, cycle: int, new_thetas: dict[tuple[int, int], float]) -> None:
        """Create theta records for new cycle.

        Args:
            cycle (int): target cycle.
            new_thetas (dict[tuple[int, int], float]): {(user, market): theta}
        """
        thetas = [
            Theta(cycle=cycle, user=user, market=market, theta=theta)
            for (user, market), theta in new_thetas.items()
        ]
        self.session.add_all(thetas)
        await self.session.commit()
