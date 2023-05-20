"""Game administration views."""
from egame179_frontend.views.admin.dashboard import RootDashboard
from egame179_frontend.views.admin.markets import RootMarketsView
from egame179_frontend.views.admin.stocks import RootStocksView
from egame179_frontend.views.admin.supplies import RootSuppliesView

__all__ = [
    "RootDashboard",
    "RootMarketsView",
    "RootStocksView",
    "RootSuppliesView",
]
