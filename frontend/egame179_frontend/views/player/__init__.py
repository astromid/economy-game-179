"""User views."""
from egame179_frontend.views.player.manufacturing import ManufacturingView
from egame179_frontend.views.player.markets import MarketsView
from egame179_frontend.views.player.overview import PlayerDashboard

__all__ = [
    "PlayerDashboard",
    "ManufacturingView",
    "MarketsView",
]
