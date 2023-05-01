from fastapi.routing import APIRouter

from egame179_backend.api.auth import router as auth_router
from egame179_backend.api.balance import router as balance_router
from egame179_backend.api.cycle import router as cycle_router
from egame179_backend.api.cycle_params import router as cycle_params_router
from egame179_backend.api.market import router as market_router
from egame179_backend.api.monitoring import router as monitoring_router
from egame179_backend.api.price import router as price_router
from egame179_backend.api.transaction import router as transaction_router

api_router = APIRouter()
api_router.include_router(auth_router, tags=["auth"])
api_router.include_router(balance_router, prefix="/balance", tags=["balance"])
api_router.include_router(cycle_router, prefix="/cycle", tags=["cycle"])
api_router.include_router(cycle_params_router, tags=["cycle_params"])
api_router.include_router(market_router, prefix="/market", tags=["market"])
api_router.include_router(monitoring_router)
api_router.include_router(price_router, prefix="/price", tags=["price"])
api_router.include_router(transaction_router, prefix="/transaction", tags=["transaction"])
