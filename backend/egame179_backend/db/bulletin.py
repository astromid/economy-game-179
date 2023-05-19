import random
from datetime import datetime

from fastapi import Depends
from sqlmodel import Field, SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from egame179_backend.db.session import get_db_session

BULLETIN_TEMPLATES = (
    "Новая сделка на рынке {market}: корпорация {user} заключила контракт на продажу {quantity} товаров.",
    "{quantity} единиц продукции {market} поступают на склад корпорации {user} и скоро будут доступны на рынке.",
    "Корпорация {user} с гордостью заявила о поставке {quantity} высококачественных единиц {market}.",
    "Аналитики ожидают появление на рынке {market} {quantity} единиц товара от корпорации {user}.",
    "Согласно отчетности корпорации {user}, на рынок {market} поступило {quantity} единиц товара.",
    "{user} заключила контракт на поставку {quantity} единиц товара на рынок {market}.",
    "Биржа {market} сообщает о поставке {quantity} единиц товара от корпорации {user}.",
    "Независимый эксперт считает, что корпорация {user} поставит на рынок {market} {quantity} единиц товара.",
    "По мере поступления новых данных, аналитики уточняют прогнозы поставок {quantity} {market} от корпорации {user}.",
    "{market} ожидает поставку {quantity} единиц товара от корпорации {user}.",
    "{quantity} единиц товара от корпорации {user} могут поступить на рынок {market}.",
    "Центр аналитики сообщает, что корпорация {user} может поставить на рынок {market} {quantity} единиц товара.",
)


class Bulletin(SQLModel, table=True):
    """Bulletins table."""

    __tablename__ = "bulletins"  # type: ignore

    id: int = Field(default=None, primary_key=True)
    ts: datetime
    cycle: int
    text: str


class BulletinDAO:
    """Class for accessing bulletins table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def select(self, cycle: int) -> list[Bulletin]:
        """Get information bulletins for cycle.

        Args:
            cycle (int): target cycle.

        Returns:
            list[Bulletin]: supply information bulletins.
        """
        query = select(Bulletin).where(Bulletin.cycle == cycle).order_by(Bulletin.id)
        raw_bulletins = await self.session.exec(query)  # type: ignore
        return raw_bulletins.all()

    async def create(self, cycle: int, user: str, market: str, quantity: int) -> None:
        """Create new information bulletin.

        Args:
            cycle (int): bulletin cycle.
            user (str): bulletin user name.
            market (str): bulletin market.
            quantity (int): bulletin quantity (noised).
        """
        template = random.choice(BULLETIN_TEMPLATES)  # noqa: S311
        text = template.format(market=market, user=user, quantity=quantity)
        self.session.add(Bulletin(ts=datetime.now(), cycle=cycle, text=text))
        await self.session.commit()
