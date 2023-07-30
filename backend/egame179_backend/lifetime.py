from collections.abc import Awaitable, Callable

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel import create_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from egame179_backend.settings import settings


def _setup_db(app: FastAPI) -> None:
    """Create connection to the database.

    This function creates SQLAlchemy engine instance, session_factory for creating sessions
        and stores them in the application's state property.

    Args:
        app (FastAPI): FastAPI application.
    """
    engine = AsyncEngine(create_engine(str(settings.db_url), echo=settings.db_echo, future=True))
    app.state.db_engine = engine
    app.state.db_session_factory = sessionmaker(
        engine,
        autocommit=False,
        autoflush=False,
        class_=AsyncSession,
        expire_on_commit=False,
    )


def startup(app: FastAPI) -> Callable[[], Awaitable[None]]:
    """Actions to run on application startup.

    This function use FastAPI app to store data, such as db_engine.

    Args:
        app (FastAPI): the FastAPI application.

    Returns:
        Callable: function that actually performs actions.
    """

    async def _startup() -> None:  # noqa: WPS430
        _setup_db(app)

    return _startup


def shutdown(app: FastAPI) -> Callable[[], Awaitable[None]]:
    """Actions to run on application's shutdown.

    Args:
        app (FastAPI): FastAPI application.

    Returns:
        Callable: function that actually performs actions.
    """

    async def _shutdown() -> None:  # noqa: WPS430
        await app.state.db_engine.dispose()

    return _shutdown
