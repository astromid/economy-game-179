"""API for communicate with backend."""
from egame179_frontend.api.balance import BalanceAPI
from egame179_frontend.api.cycle import CycleAPI
from egame179_frontend.api.market import MarketAPI
from egame179_frontend.api.price import PriceAPI
from egame179_frontend.api.product import ProductAPI
from egame179_frontend.api.stocks import StocksAPI
from egame179_frontend.api.supply import SupplyAPI
from egame179_frontend.api.transaction import TransactionAPI
from egame179_frontend.api.user import AuthAPI

__all__ = [
    "BalanceAPI",
    "CycleAPI",
    "MarketAPI",
    "PriceAPI",
    "ProductAPI",
    "StocksAPI",
    "SupplyAPI",
    "TransactionAPI",
    "AuthAPI",
]
