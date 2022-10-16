from fastapi.routing import APIRouter

from egame179_backend.app.api import auth, echo, monitoring

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(echo.router, prefix="/echo", tags=["echo"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
