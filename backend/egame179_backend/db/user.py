from fastapi import Depends
from passlib.context import CryptContext
from sqlmodel import Field, SQLModel, or_, select
from sqlmodel.ext.asyncio.session import AsyncSession

from egame179_backend.db.session import get_db_session


class User(SQLModel, table=True):
    """Users table."""

    __tablename__ = "users"  # type: ignore

    id: int = Field(primary_key=True)
    role: str
    name: str
    login: str | None
    password: str | None


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

    async def get_by_name(self, name: str) -> User | None:
        """Get user info by name.

        Args:
            name (str): user name.

        Returns:
            User | None: user info or None if user not found.
        """
        query = select(User).where(User.name == name)
        raw_user = await self.session.exec(query)  # type: ignore
        return raw_user.one_or_none()

    async def get_names(self) -> dict[int, str]:
        """Get players & NPCs name mapping.

        Returns:
            dict[int, str]: {user: name}
        """
        query = select(User).where(or_(User.role == "player", User.role == "npc"))  # type: ignore
        raw_users = await self.session.exec(query)  # type: ignore
        return {user.id: user.name for user in raw_users.all()}
