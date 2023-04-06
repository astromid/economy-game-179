from fastapi import Depends
from passlib.context import CryptContext
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from egame179_backend.db.dependencies import get_db_session
from egame179_backend.db.models import User


class UserDAO:
    """Class for accessing users table."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def check_credentials(self, login: str, password: str) -> User | None:
        """Find user in database by login and password.

        Args:
            login (str): user login.
            password (str): user password.

        Returns:
            User | None: user information or None if credentials are incorrect.
        """
        query = select(User).where(User.login == login)
        raw_user = await self.session.exec(query)  # type: ignore
        user: User | None = raw_user.one_or_none()
        if user is not None:
            if self.pwd_context.verify(password, user.password):
                return user
        return None

    async def get_user_by_name(self, name: str) -> User | None:
        """Get user info by name.

        Args:
            name (str): user name.

        Returns:
            User | None: user info or None if user not found.
        """
        query = select(User).where(User.name == name)
        raw_user = await self.session.exec(query)  # type: ignore
        return raw_user.one_or_none()
