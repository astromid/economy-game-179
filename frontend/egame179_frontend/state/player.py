from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass
from typing import Any

import networkx as nx
import pandas as pd

from egame179_frontend import api
from egame179_frontend.api.cycle import Cycle


@dataclass
class PlayerState:  # noqa: WPS214
    """Player game state."""

    user_id: int
    cycle: Cycle
    _players: dict[int, str] | None = None
    _markets: nx.Graph | None = None
    _balances: list[float] | None = None
    _cycle_params: dict[str, float | int] | None = None
    _transactions: list[dict[str, Any]] | None = None
    _unlocked_markets: list[int] | None = None
    _prices: pd.DataFrame | None = None
    _demand_factors: dict[int, float] | None = None
    _products: list[dict[str, Any]] | None = None
    _thetas: dict[int, float] | None = None
    _storage: dict[int, int] | None = None
    _shares: dict[int, list[tuple[str, float | None]]] | None = None
    _detailed_markets: nx.Graph | None = None

    @property
    def players(self) -> dict[int, str]:
        """Mapping user_id -> player name.

        Returns:
            dict[int, str]: mapping for players.
        """
        if self._players is None:
            self._players = {user.id: user.name for user in api.AuthAPI.get_players()}
        return self._players

    @property
    def markets(self) -> nx.Graph:
        """Markets graph.

        Returns:
            nx.Graph: markets graph.
        """
        if self._markets is None:
            self._markets = nx.Graph()
            for market in api.MarketAPI.get_markets():
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
            self._balances = [bal.amount for bal in api.BalanceAPI.get_user_balances()]
        return self._balances

    @property
    def cycle_params(self) -> dict[str, float | int]:
        """Cycle parameters (alpha, beta, gamma, tau_s).

        Returns:
            dict[str, float | int]: alpha, beta, gamma & tau_s parameters.
        """
        if self._cycle_params is None:
            self._cycle_params = api.CycleAPI.get_cycle_parameters().dict()
        return self._cycle_params

    @property
    def transactions(self) -> list[dict[str, Any]]:
        """Player transactions.

        Returns:
            list[dict[str, Any]]: player transactions.
        """
        if self._transactions is None:
            self._transactions = [tr.dict() for tr in api.TransactionAPI.get_user_transactions()]
        return self._transactions

    @property
    def unlocked_markets(self) -> list[int]:
        """Unlocked markets for player.

        Returns:
            list[int]: list of unlocked market ids.
        """
        if self._unlocked_markets is None:
            self._unlocked_markets = [um.market_id for um in api.MarketAPI.get_user_unlocked_markets()]
        return self._unlocked_markets

    @property
    def prices(self) -> pd.DataFrame:
        """Buy & sell prices history for all markets.

        Returns:
            pd.DataFrame: pandas dataframe with columns (cycle, market_id, buy, sell)
        """
        if self._prices is None:
            self._prices = pd.DataFrame([price.dict() for price in api.PriceAPI.get_market_prices()])
        return self._prices

    @property
    def demand_factors(self) -> dict[int, float]:
        """Demand factors for all markets.

        Returns:
            dict[int, float]: dict {market_id: demand_factor}.
        """
        if self._demand_factors is None:
            self._demand_factors = {df.market_id: df.factor for df in api.CycleAPI.get_demand_factors()}
        return self._demand_factors

    @property
    def products(self) -> list[dict[str, Any]]:
        """All user products.

        Returns:
            list[dict[str, Any]]: list of dicts with product info.
        """
        if self._products is None:
            self._products = [product.dict() for product in api.ProductAPI.get_user_products()]
        return self._products

    @property
    def thetas(self) -> dict[int, float]:
        """Current theta.

        Returns:
            dict[int, float]: {market_id: theta}
        """
        if self._thetas is None:
            self._thetas = {
                product["market_id"]: product["theta"]
                for product in self.products
                if product["cycle"] == self.cycle.cycle
            }
        return self._thetas

    @property
    def storage(self) -> dict[int, int]:
        """Current storage.

        Returns:
            dict[int, int]: {market_id: storage}
        """
        if self._storage is None:
            self._storage = {
                product["market_id"]: product["storage"]
                for product in self.products
                if product["cycle"] == self.cycle.cycle
            }
        return self._storage

    @property
    def shares(self) -> dict[int, list[tuple[str, float | None]]]:
        """Market shares, visible for player.

        Returns:
            dict[int, list[tuple[str, float | None]]]: {market_id: [(user_name, share %)]}.
        """
        if self._shares is None:
            self._shares = defaultdict(list)
            for share in api.ProductAPI.get_shares():
                player = self.players[share.user_id]
                self._shares[share.market_id].append((player, share.share))
        return self._shares

    @property
    def detailed_markets(self) -> nx.Graph:
        """Markets graph with additional info.

        Returns:
            nx.Graph: networkx graph with node attributes.
        """
        if self._detailed_markets is None:
            graph = deepcopy(self.markets)
            last_prices = self.prices[self.prices["cycle"] == self.cycle.cycle].set_index("market_id")
            for node_id, node in graph.nodes.items():
                node["buy"] = last_prices.loc[node_id, "buy"]
                node["sell"] = last_prices.loc[node_id, "sell"]
                node["demand_factor"] = self.demand_factors[node_id]
                node["storage"] = self.storage[node_id]
                # default top shares values
                node["top1"] = "None"
                node["top2"] = "None"
                market_shares = self.shares[node_id]
                for idx, share in enumerate(market_shares[:2], start=1):
                    player, percent = share
                    percent_repr = f"{percent:.2%}" if percent is not None else "??%"
                    node[f"top{idx}"] = f"{player}: {percent_repr}"
            self._detailed_markets = graph
        return self._detailed_markets

    @property
    def supplies(self) -> list[dict[str, Any]]:
        """All user supplies on current cycle.

        Returns:
            list[dict[str, Any]]: list of dicts with supply info.
        """
        # we do not cache supplies, because they are changing in real time
        return [supply.dict() for supply in api.SupplyAPI.get_user_supplies()]

    def clear_after_buy(self) -> None:
        """Clean invalid caches after buy operation."""
        self._balances = None
        self._products = None
        self._storage = None
        self._transactions = None

    def clear_after_supply(self) -> None:
        """Clean invalid caches after supply operation."""
        self._products = None
        self._storage = None
