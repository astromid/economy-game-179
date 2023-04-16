"""Communication with database module."""
from collections.abc import AsyncGenerator

from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.requests import Request


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """Create and get database session.

    Args:
        request (Request): current request.

    Yields:
        AsyncSession: database session.
    """
    session: AsyncSession = request.app.state.db_session_factory()
    async with session:
        yield session
