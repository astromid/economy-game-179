from fastapi import Depends
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from egame179_backend.db.session import get_db_session


class Warehouse(SQLModel, table=True):
    """Warehouses table."""

    __tablename__ = "warehouses"  # type: ignore

    cycle: int
    user: int
    market: int
    quantity: int


class WarehouseDAO:
    """Class for accessing warehouses table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def get(self, user: int, cycle: int, market: int) -> int:
        """Get amount of items in user warehouse.

        Args:
            user (int): target user id.
            cycle (int): target cycle.
            market (int): target market.

        Returns:
            int: amount of items.
        """
        query = select(Warehouse).where(
            Warehouse.user == user,
            Warehouse.cycle == cycle,
            Warehouse.market == market,
        )
        raw_warehouse = await self.session.exec(query)  # type: ignore
        return raw_warehouse.one().quantity

    async def select(self, user: int | None = None, cycle: int | None = None) -> list[Warehouse]:
        """Get user storages.

        Args:
            user (int, optional): target user id. If None, all user balances return.
            cycle (int): target cycle. If None, all cycles return.

        Returns:
            list[Warehouse]: list of warehouse records.
        """
        query = select(Warehouse).order_by(Warehouse.cycle)
        if user is not None:
            query = query.where(Warehouse.user == user)
        if cycle is not None:
            query = query.where(Warehouse.cycle == cycle)
        raw_warehouses = await self.session.exec(query)  # type: ignore
        return raw_warehouses.all()
