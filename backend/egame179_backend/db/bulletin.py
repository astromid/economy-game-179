from datetime import datetime

import numpy as np
from fastapi import Depends
from sqlmodel import Field, SQLModel, col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from egame179_backend.db.session import get_db_session

BULLETIN_TEMPLATES = (
    "Новая сделка на рынке <b>{market}</b>: корпорация <b>{user}</b> заключила контракт на продажу <b>{quantity}</b> товаров.",
    "<b>{quantity}</b> единиц продукции <b>{market}</b> поступают на склад корпорации <b>{user}</b> и скоро будут доступны на рынке.",
    "Корпорация <b>{user}</b> с гордостью заявила о поставке <b>{quantity}</b> высококачественных единиц <b>{market}</b>.",
    "Аналитики ожидают появление на рынке <b>{market}</b> <b>{quantity}</b> единиц товара от корпорации <b>{user}</b>.",
    "Согласно отчетности корпорации <b>{user}</b>, на рынок <b>{market}</b> поступило <b>{quantity}</b> единиц товара.",
    "<b>{user}</b> заключила контракт на поставку <b>{quantity}</b> единиц товара на рынок <b>{market}</b>.",
    "Биржа <b>{market}</b> сообщает о поставке <b>{quantity}</b> единиц товара от корпорации <b>{user}</b>.",
    "Независимый эксперт считает, что корпорация <b>{user}</b> поставит на рынок <b>{market}</b> <b>{quantity}</b> единиц товара.",
    "По мере поступления новых данных, аналитики уточняют прогнозы поставок <b>{quantity}</b> <b>{market}</b> от корпорации <b>{user}</b>.",
    "<b>{market}</b> ожидает поставку <b>{quantity}</b> единиц товара от корпорации <b>{user}</b>.",
    "<b>{quantity}</b> единиц товара от корпорации <b>{user}</b> могут поступить на рынок <b>{market}</b>.",
    "Центр аналитики сообщает, что корпорация <b>{user}</b> может поставить на рынок <b>{market}</b> <b>{quantity}</b> единиц товара.",
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
        query = select(Bulletin).where(Bulletin.cycle == cycle).order_by(col(Bulletin.id).desc())
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
        template = np.random.choice(BULLETIN_TEMPLATES)  # noqa: S311
        text = template.format(market=market, user=user, quantity=quantity)
        self.session.add(Bulletin(ts=datetime.now(), cycle=cycle, text=text))
        await self.session.commit()
