from dataclasses import dataclass

import networkx as nx

from egame179_frontend.api.cycle import Cycle


@dataclass
class RootState:
    """Root game state."""

    cycle: Cycle
    _markets: nx.Graph | None = None
