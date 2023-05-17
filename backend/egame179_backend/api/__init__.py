"""egame179_backend API package."""
from fastapi.routing import APIRouter

from egame179_backend.api.auth import router as auth_router
from egame179_backend.api.balance import router as balance_router
from egame179_backend.api.bulletin import router as bulletin_router
from egame179_backend.api.cycle import router as cycle_router
from egame179_backend.api.market import router as market_router
from egame179_backend.api.market_price import router as price_router
from egame179_backend.api.modificators import router as modificators_router
from egame179_backend.api.monitoring import router as monitoring_router
from egame179_backend.api.production import router as production_router
from egame179_backend.api.stocks import router as stocks_router
from egame179_backend.api.supply import router as supply_router
from egame179_backend.api.transaction import router as transaction_router
from egame179_backend.api.warehouse import router as warehouse_router

api_router = APIRouter()
api_router.include_router(auth_router, tags=["auth"])
api_router.include_router(balance_router, prefix="/balance", tags=["balance"])
api_router.include_router(bulletin_router, prefix="/bulletin", tags=["bulletin"])
api_router.include_router(cycle_router, prefix="/cycle", tags=["cycle"])
api_router.include_router(market_router, prefix="/market", tags=["market"])
api_router.include_router(modificators_router, prefix="/modificators", tags=["modificators"])
api_router.include_router(monitoring_router, tags=["monitoring"])
api_router.include_router(price_router, tags=["market"])
api_router.include_router(production_router, prefix="/production", tags=["product"])
api_router.include_router(stocks_router, prefix="/stocks", tags=["stocks"])
api_router.include_router(supply_router, prefix="/supply", tags=["supply"])
api_router.include_router(transaction_router, prefix="/transaction", tags=["transaction"])
api_router.include_router(warehouse_router, prefix="/warehouse", tags=["warehouse"])
