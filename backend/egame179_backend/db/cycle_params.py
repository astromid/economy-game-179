from fastapi import Depends
from sqlmodel import Field, SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from egame179_backend.db import get_db_session


class CycleParams(SQLModel, table=True):
    """Cycle parameters table."""

    __tablename__ = "cycle_params"  # type: ignore

    cycle: int = Field(default=None, primary_key=True)
    alpha: float
    beta: float
    gamma: float
    tau_s: int
    coeff_h: int
    coeff_k: int
    coeff_l: int
    demand_ring2: int
    demand_ring1: int
    demand_ring0: int


class CycleParamsDAO:
    """Class for accessing cycle parameters table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def get(self, cycle: int) -> CycleParams:
        """Get parameters for target cycle.

        Args:
            cycle (int): target cycle.

        Returns:
            CycleParams: target cycle parameters.
        """
        query = select(CycleParams).where(CycleParams.cycle == cycle)
        raw_params = await self.session.exec(query)  # type: ignore
        return raw_params.one()
