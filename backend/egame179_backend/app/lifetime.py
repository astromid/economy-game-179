from asyncio import current_task
from collections.abc import Awaitable, Callable

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session, create_async_engine
from sqlalchemy.orm import sessionmaker

from egame179_backend.settings import settings


def _setup_db(app: FastAPI) -> None:
    """Create connection to the database.

    This function creates SQLAlchemy engine instance, session_factory for creating sessions
        and stores them in the application's state property.

    Args:
        app (FastAPI): fastAPI application.
    """
    engine = create_async_engine(str(settings.db_url), echo=settings.db_echo)
    session_factory = async_scoped_session(
        sessionmaker(
            engine,
            expire_on_commit=False,
            class_=AsyncSession,  # type: ignore
        ),
        scopefunc=current_task,
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
