from fastapi import Depends
from sqlmodel import Field, SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from egame179_backend.db import get_db_session


class Product(SQLModel, table=True):
    """Products table."""

    __tablename__ = "products"  # type: ignore

    cycle: int = Field(primary_key=True)
    user_id: int = Field(primary_key=True)
    market_id: int = Field(primary_key=True)
    storage: int
    theta: float
    share: float


class ProductDAO:
    """Class for accessing products table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def get(self, user_id: int | None = None) -> list[Product]:
        """Get all products for particular user.

        Args:
            user_id (int, optional): target user id. If None, return products for all users.

        Returns:
            list[Product]: product records.
        """
        query = select(Product).order_by(Product.cycle)
        if user_id is not None:
            query = query.where(Product.user_id == user_id)
        raw_products = await self.session.exec(query)  # type: ignore
        return raw_products.all()

    async def create(  # noqa: WPS211
        self,
        cycle: int,
        user_id: int,
        market_id: int,
        storage: int,
        theta: float,
        share: float,
    ) -> None:
        """Create new product record.

        Args:
            cycle (int): target cycle.
            user_id (int): target user id.
            market_id (int): target market id.
            storage (int): storages.
            theta (float): manufacturing theta.
            share (float): market share.
        """
        self.session.add(
            Product(
                cycle=cycle,
                user_id=user_id,
                market_id=market_id,
                storage=storage,
                theta=theta,
                share=share,
            ),
        )
        await self.session.commit()

    async def update_storage(self, cycle: int, user_id: int, market_id: int, delta: int) -> None:
        """Update player storage.

        Args:
            cycle (int): target cycle.
            user_id (int): target user id.
            market_id (int): target market id.
            delta (int): delta storage amount (add up to existing amount).
        """
        query = select(Product).where(
            Product.cycle == cycle,
            Product.user_id == user_id,
            Product.market_id == market_id,
        )
        raw_product = await self.session.exec(query)  # type: ignore
        product: Product = raw_product.one()
        product.storage += delta
        self.session.add(product)
        await self.session.commit()

    async def update_theta(self, cycle: int, user_id: int, market_id: int, theta: float) -> None:
        """Update player theta.

        Args:
            cycle (int): target cycle.
            user_id (int): target user id.
            market_id (int): target market id.
            theta (float): new product theta.
        """
        query = select(Product).where(
            Product.cycle == cycle,
            Product.user_id == user_id,
            Product.market_id == market_id,
        )
        raw_product = await self.session.exec(query)  # type: ignore
        product: Product = raw_product.one()
        product.theta = theta
        self.session.add(product)
        await self.session.commit()
