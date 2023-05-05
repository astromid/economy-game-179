from dataclasses import dataclass
from typing import Any

import networkx as nx
import pandas as pd

from egame179_frontend.api.balance import BalanceAPI
from egame179_frontend.api.cycle import Cycle
from egame179_frontend.api.cycle_params import CycleParamsAPI
from egame179_frontend.api.market import MarketAPI
from egame179_frontend.api.price import PriceAPI
from egame179_frontend.api.transaction import TransactionAPI


@dataclass
class PlayerState:
    """Player game state."""

    cycle: Cycle
    _markets: nx.Graph | None = None
    _balances: list[float] | None = None
    _cycle_params: dict[str, float | int] | None = None
    _transactions: list[dict[str, Any]] | None = None
    _unlocked_markets: list[int] | None = None
    _prices: pd.DataFrame | None = None

    @property
    def markets(self) -> nx.Graph:
        """Markets graph.

        Returns:
            nx.Graph: markets graph.
        """
        if self._markets is None:
            self._markets = nx.Graph()  # noqa: WPS601
            for market in MarketAPI.get_markets():
                self._markets.add_node(market.id, name=market.name, ring=market.ring)
                self._markets.add_edges_from([
                    (market.id, market.link1),
                    (market.id, market.link2),
                    (market.id, market.link3),
                ])
                if market.link4 is not None:
                    self._markets.add_edge(market.id, market.link4)
                if market.link5 is not None:
                    self._markets.add_edge(market.id, market.link5)
        return self._markets

    @property
    def balances(self) -> list[float]:
        """Player balances history.

        Returns:
            list[float]: balances ordered by cycle.
        """
        if self._balances is None:
            self._balances = [bal.amount for bal in BalanceAPI.get_user_balances()]  # noqa: WPS601
        return self._balances

    @property
    def cycle_params(self) -> dict[str, float | int]:
        """Cycle parameters (alpha, beta, gamma, tau_s).

        Returns:
            dict[str, float | int]: alpha, beta, gamma & tau_s parameters.
        """
        if self._cycle_params is None:
            self._cycle_params = CycleParamsAPI.get_cycle_parameters().dict()  # noqa: WPS601
        return self._cycle_params

    @property
    def transactions(self) -> list[dict[str, Any]]:
        """Player transactions.

        Returns:
            list[dict[str, Any]]: player transactions.
        """
        if self._transactions is None:
            self._transactions = [tr.dict() for tr in TransactionAPI.get_user_transactions()]  # noqa: WPS601
        return self._transactions

    @property
    def unlocked_markets(self) -> list[int]:
        """Unlocked markets for player.

        Returns:
            list[int]: list of unlocked market ids.
        """
        if self._unlocked_markets is None:
            self._unlocked_markets = [um.market_id for um in MarketAPI.get_user_unlocked_markets()]  # noqa: WPS601
        return self._unlocked_markets

    @property
    def prices(self) -> pd.DataFrame:
        """Buy & sell prices history for all markets.

        Returns:
            pd.DataFrame: pandas dataframe with columns (cycle, market_id, buy, sell)
        """
        if self._prices is None:
            self._prices = pd.DataFrame([price.dict() for price in PriceAPI.get_market_prices()])  # noqa: WPS601
        return self._prices
