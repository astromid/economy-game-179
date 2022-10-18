from fastapi import Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from egame179_backend.db.dependencies import get_db_session
from egame179_backend.db.models import User


class UserDAO:
    """Class for accessing users table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def auth(self, login: str, password: str) -> User | None:
        query = select(User).where(User.login == login, User.password == password)
        raw_user = await self.session.exec(query)  # type: ignore
        return raw_user.one_or_none()
