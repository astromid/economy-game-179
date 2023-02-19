from fastapi.routing import APIRouter

from egame179_backend.app.api import auth, balance, cycle, monitoring

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(cycle.router, prefix="/cycle", tags=["cycle"])
api_router.include_router(balance.router, prefix="/balance", tags=["balance"])
