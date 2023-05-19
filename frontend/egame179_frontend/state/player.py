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

    user: int
    cycle: Cycle
    _names: dict[int, str] | None = None
    _player_ids: list[int] | None = None
    _markets: nx.Graph | None = None
    _balances: list[float] | None = None
    _transactions: list[dict[str, Any]] | None = None
    _unlocked_markets: list[int] | None = None
    _prices: pd.DataFrame | None = None
    _demand_factors: dict[int, float] | None = None
    _production: list[dict[str, Any]] | None = None
    _thetas: dict[int, float] | None = None
    _storage: dict[int, int] | None = None
    _shares: dict[tuple[int, int], tuple[int, float | None]] | None = None
    _stocks: pd.DataFrame | None = None
    _detailed_markets: nx.Graph | None = None

    @property
    def names(self) -> dict[int, str]:
        """Get mapping user_id -> player name.

        Returns:
            dict[int, str]: mapping for players.
        """
        if self._names is None:
            self._names = api.AuthAPI.get_names()
        return self._names

    @property
    def player_ids(self) -> list[int]:
        """Player ids.

        Returns:
            list[int]: player ids.
        """
        if self._player_ids is None:
            self._player_ids = api.AuthAPI.get_players()
        return self._player_ids

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
            self._markets.add_edges_from(api.MarketAPI.get_edges())
        return self._markets

    @property
    def balances(self) -> list[float]:
        """Player balances history.

        Returns:
            list[float]: balances ordered by cycle.
        """
        if self._balances is None:
            self._balances = [bal.balance for bal in api.BalanceAPI.get_user_balances()]
        return self._balances

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
            self._unlocked_markets = api.MarketAPI.get_unlocked_markets()
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
            self._demand_factors = api.MarketAPI.get_demand_factors()
        return self._demand_factors

    @property
    def production(self) -> list[dict[str, Any]]:
        """All user production.

        Returns:
            list[dict[str, Any]]: list of dicts with product info.
        """
        if self._production is None:
            self._production = [prod.dict() for prod in api.ProductionAPI.get_user_products()]
        return self._production

    @property
    def thetas(self) -> dict[int, float]:
        """Current thetas.

        Returns:
            dict[int, float]: {market_id: theta}
        """
        if self._thetas is None:
            self._thetas = {
                theta.market: theta.theta
                for theta in api.ProductionAPI.get_user_thetas()
                if theta.cycle == self.cycle.id
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
                wh.market: wh.quantity
                for wh in api.WarehouseAPI.get_user_storage()
                if wh.cycle == self.cycle.id
            }
        return self._storage

    @property
    def shares(self) -> dict[tuple[int, int], tuple[int, float | None]]:
        """Market shares, visible for player.

        Returns:
            dict[int, list[tuple[str, float | None]]]: {market_id: [(user_name, share %)]}.
        """
        if self._shares is None:
            self._shares = {}
            for share in api.MarketAPI.get_shares_user():
                self._shares[(share.market, share.position)] = (share.user, share.share)
        return self._shares

    @property
    def detailed_markets(self) -> nx.Graph:
        """Markets graph with additional info.

        Returns:
            nx.Graph: networkx graph with node attributes.
        """
        if self._detailed_markets is None:
            graph = deepcopy(self.markets)
            for node_id, node in graph.nodes.items():
                node["demand_factor"] = self.demand_factors[node_id]
                node["storage"] = self.storage[node_id]
                for pos in (1, 2):
                    player, share = self.shares.get((node_id, pos), (None, None))
                    player_name = self.names[player] if player is not None else "None"
                    percent_repr = f"{share:.2%}" if share is not None else "??%"
                    node[f"top{pos}"] = f"{player_name}: {percent_repr}"
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

    @property
    def stocks(self) -> pd.DataFrame:
        """Stocks prices for all companies.

        Returns:
            pd.DataFrame: pandas dataframe with columns (cycle, company, price)
        """
        if self._stocks is None:
            self._stocks = pd.DataFrame([stock.dict() for stock in api.StocksAPI.get_stocks()])
            self._stocks["company"] = self._stocks["user"].map(self.names)
        return self._stocks

    def clear_after_buy(self) -> None:
        """Clean invalid caches after buy operation."""
        self._balances = None
        self._production = None
        self._storage = None
        self._transactions = None

    def clear_after_supply(self) -> None:
        """Clean invalid caches after supply operation."""
        self._balances = None
        self._storage = None
        self._transactions = None
