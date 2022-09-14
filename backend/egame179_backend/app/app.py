from importlib import metadata
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from egame179_backend.app.api.router import api_router

APP_ROOT = Path(__file__).parent.parent


def get_app() -> FastAPI:
    """Get FastAPI application.

    This is the main constructor of an application.

    Returns:
        FastAPI: application instance.
    """
    app = FastAPI(
        title="egame179_backend",
        description="FastAPI backend for economic strategy game",
        version=metadata.version("egame179_backend"),
        docs_url=None,
        redoc_url=None,
        openapi_url="/api/openapi.json",
        default_response_class=ORJSONResponse,
    )
    app.include_router(router=api_router, prefix="/api")

    return app
