"""API for communicate with backend."""
from egame179_frontend.api.balance import BalanceAPI
from egame179_frontend.api.bulletin import BulletinAPI
from egame179_frontend.api.cycle import CycleAPI
from egame179_frontend.api.market import MarketAPI
from egame179_frontend.api.modificators import ModificatorAPI
from egame179_frontend.api.price import PriceAPI
from egame179_frontend.api.production import ProductionAPI
from egame179_frontend.api.stocks import StocksAPI
from egame179_frontend.api.supply import SupplyAPI
from egame179_frontend.api.sync import SyncStatusAPI
from egame179_frontend.api.transaction import TransactionAPI
from egame179_frontend.api.user import AuthAPI
from egame179_frontend.api.warehouse import WarehouseAPI

__all__ = [
    "BalanceAPI",
    "BulletinAPI",
    "CycleAPI",
    "MarketAPI",
    "ModificatorAPI",
    "PriceAPI",
    "ProductionAPI",
    "StocksAPI",
    "SupplyAPI",
    "SyncStatusAPI",
    "TransactionAPI",
    "AuthAPI",
    "WarehouseAPI",
]
