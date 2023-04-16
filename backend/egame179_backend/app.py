from importlib import metadata

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from egame179_backend.api.router import api_router
from egame179_backend.lifetime import shutdown, startup


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
        redoc_url=None,
        openapi_url="/api/openapi.json",
        default_response_class=ORJSONResponse,
    )
    app.on_event("startup")(startup(app))
    app.on_event("shutdown")(shutdown(app))
    app.include_router(api_router, prefix="/api")
    return app
