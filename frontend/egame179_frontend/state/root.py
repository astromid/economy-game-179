from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass
from typing import Any

import networkx as nx
import pandas as pd

from egame179_frontend import api
from egame179_frontend.api.cycle import Cycle
from egame179_frontend.style import PlayerColors


@dataclass
class RootState:  # noqa: WPS214
    """Root game state."""

    cycle: Cycle
    _names: dict[int, str] | None = None
    _player_ids: list[int] | None = None
    _player_colors: dict[int, str] | None = None
    _sync_status: dict[int, bool] | None = None
    _markets: nx.Graph | None = None
    _modificators: list[dict[str, Any]] | None = None
    _balances: list[float] | None = None
    _transactions: list[dict[str, Any]] | None = None
    _prices: pd.DataFrame | None = None
    _demand_factors: dict[int, float] | None = None
    _production: list[dict[str, Any]] | None = None
    _thetas: dict[int, float] | None = None
    _storage: dict[int, list[dict[str, Any]]] | None = None
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
    def player_colors(self) -> dict[int, str]:
        if self._player_colors is None:
            self._player_colors = {user: color for user, color in zip(self.player_ids, PlayerColors)}
        return self._player_colors

    @property
    def sync_status(self) -> dict[int, bool]:
        if self._sync_status is None:
            self._sync_status = api.SyncStatusAPI.get_sync_status()
        return self._sync_status

    @property
    def markets(self) -> nx.Graph:
        """Markets graph.

        Returns:
            nx.Graph: markets graph.
        """
        if self._markets is None:
            self._markets = nx.Graph()
            for market in api.MarketAPI.get_markets():
                self._markets.add_node(market.id, name=market.name, ring=market.ring, home_user=market.home_user)
            self._markets.add_edges_from(api.MarketAPI.get_edges())
        return self._markets

    @property
    def modificators(self) -> list[dict[str, Any]]:
        """Player fee modificators.

        Returns:
            dict[str, float]: fee coeffs.
        """
        if self._modificators is None:
            self._modificators = [mod.dict() for mod in api.ModificatorAPI.get_modificators()]
        return self._modificators

    @property
    def balances(self) -> list[float]:
        """Player balances history.

        Returns:
            list[float]: balances ordered by cycle.
        """
        if self._balances is None:
            self._balances = [bal.balance for bal in api.BalanceAPI.get_balances()]
        return self._balances

    @property
    def transactions(self) -> list[dict[str, Any]]:
        """Player transactions.

        Returns:
            list[dict[str, Any]]: player transactions.
        """
        if self._transactions is None:
            self._transactions = [tr.dict() for tr in api.TransactionAPI.get_transactions()]
        return self._transactions

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
            self._production = [prod.dict() for prod in api.ProductionAPI.get_products()]
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
                for theta in api.ProductionAPI.get_thetas()
                if theta.cycle == self.cycle.id
            }
        return self._thetas

    @property
    def storage(self) -> dict[int, list[dict[str, Any]]]:
        if self._storage is None:
            self._storage = defaultdict(list)
            for wh in api.WarehouseAPI.get_storages():
                if wh.cycle == self.cycle.id and wh.quantity > 0:
                    self._storage[wh.market].append(wh.dict())
        return self._storage

    @property
    def total_storage(self) -> dict[int, int]:
        total = {}
        for market, storages in self.storage.items():
            total[market] = sum([wh["quantity"] for wh in storages])
        return total

    @property
    def shares(self) -> dict[tuple[int, int], tuple[int, float | None]]:
        """Market shares, visible for player.

        Returns:
            dict[tuple[int, int], tuple[int, float | None]]: {(market_id, position): (user_id, share)}
        """
        if self._shares is None:
            self._shares = {}
            for share in api.MarketAPI.get_shares():
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
                node["storage"] = self.total_storage.get(node_id, 0)
                node["owner"] = self.shares.get((node_id, 1), (None, None))[0]
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
        return [supply.dict() for supply in api.SupplyAPI.get_supplies()]

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
