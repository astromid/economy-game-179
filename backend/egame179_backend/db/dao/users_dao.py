from fastapi import Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from egame179_backend.db.dependencies import get_db_session
from egame179_backend.db.models import User


class UserDAO:
    """Class for accessing users table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def get_all_users(self) -> list[User]:
        query = select(User)
        raw_users = await self.session.execute(query)
        return raw_users.scalars().all()

    async def auth_user(self, login: str, password: str) -> User | None:
        query = select(User).where(User.login == login, User.password == password)
        raw_user = await self.session.execute(query)
        return raw_user.scalars().one_or_none()
