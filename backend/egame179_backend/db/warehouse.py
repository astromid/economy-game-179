from fastapi import Depends
from sqlmodel import Field, SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from egame179_backend.db.session import get_db_session


class Warehouse(SQLModel, table=True):
    """Warehouses table."""

    __tablename__ = "warehouses"  # type: ignore

    cycle: int = Field(primary_key=True)
    user: int = Field(primary_key=True)
    market: int = Field(primary_key=True)
    quantity: int


class WarehouseDAO:
    """Class for accessing warehouses table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def get(self, cycle: int, user: int, market: int) -> int:
        """Get amount of items in user warehouse.

        Args:
            cycle (int): target cycle.
            user (int): target user id.
            market (int): target market.

        Returns:
            int: amount of items.
        """
        query = select(Warehouse).where(
            Warehouse.cycle == cycle,
            Warehouse.user == user,
            Warehouse.market == market,
        )
        raw_warehouse = await self.session.exec(query)  # type: ignore
        warehouse = raw_warehouse.one_or_none()
        # quantity is Decimal I don't know why
        return 0 if warehouse is None else int(warehouse.quantity)

    async def select(self, cycle: int | None = None, user: int | None = None) -> list[Warehouse]:
        """Get user storages.

        Args:
            cycle (int): target cycle. If None, all cycles return.
            user (int, optional): target user id. If None, all user storages return.

        Returns:
            list[Warehouse]: list of non-zero warehouse records.
        """
        query = select(Warehouse).order_by(Warehouse.cycle)
        if user is not None:
            query = query.where(Warehouse.user == user)
        if cycle is not None:
            query = query.where(Warehouse.cycle == cycle)
        raw_warehouses = await self.session.exec(query)  # type: ignore
        warehouses = raw_warehouses.all()
        for warehouse in warehouses:
            # quantity is Decimal I don't know why
            warehouse.quantity = int(warehouse.quantity)
        return warehouses
