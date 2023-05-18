from fastapi import Depends
from sqlmodel import Field, SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from egame179_backend.db.session import get_db_session


class WorldDemand(SQLModel, table=True):
    """World demand table."""

    __tablename__ = "world_demand"  # type: ignore

    cycle: int = Field(primary_key=True)
    ring: int = Field(primary_key=True)
    demand_pm: float


class WorldDemandDAO:
    """Class for accessing world demand table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def select(self, cycle: int) -> dict[int, int]:
        """Get world demand on particular cycle.

        Args:
            cycle (int): target cycle.

        Returns:
            dict[int, int]: {ring: demand}
        """
        query = select(WorldDemand).where(WorldDemand.cycle == cycle)
        raw_demands = await self.session.exec(query)  # type: ignore
        return {demand.ring: demand.demand_pm for demand in raw_demands.all()}
