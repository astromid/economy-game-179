from collections.abc import Awaitable, Callable

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel import create_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from egame179_backend.settings import Settings


def _setup_db(app: FastAPI) -> None:
    """Create connection to the database.

    This function creates SQLAlchemy engine instance, session_factory for creating sessions
        and stores them in the application's state property.

    Args:
        app (FastAPI): fastAPI application.
    """
    settings = Settings()

    engine = AsyncEngine(create_engine(str(settings.db_url), echo=settings.db_echo, future=True))
    session_factory = sessionmaker(
        engine,
        autocommit=False,
        autoflush=False,
        class_=AsyncSession,  # type: ignore
        expire_on_commit=False,
    )
    app.state.db_engine = engine
    app.state.db_session_factory = session_factory


def startup(app: FastAPI) -> Callable[[], Awaitable[None]]:
    """Actions to run on application startup.

    This function use fastAPI app to store data, such as db_engine.

    Args:
        app (FastAPI): the fastAPI application.

    Returns:
        Callable: function that actually performs actions.
    """

    async def _startup() -> None:  # noqa: WPS430
        _setup_db(app)

    return _startup


def shutdown(app: FastAPI) -> Callable[[], Awaitable[None]]:
    """Actions to run on application's shutdown.

    Args:
        app (FastAPI): fastAPI application.

    Returns:
        Callable: function that actually performs actions.
    """

    async def _shutdown() -> None:  # noqa: WPS430
        await app.state.db_engine.dispose()

    return _shutdown
