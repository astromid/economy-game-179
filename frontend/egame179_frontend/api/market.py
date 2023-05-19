"""Markets API."""
import httpx
import streamlit as st
from pydantic import BaseModel, parse_obj_as

from egame179_frontend.settings import settings


class Market(BaseModel):
    """Market model."""

    id: int
    name: str
    ring: int
    home_user: int | None


class MarketShare(BaseModel):
    """Market share with player visible info."""

    user: int
    market: int
    share: float | None = None
    position: int


class MarketAPI:
    """Market API."""

    _api_url = settings.backend_url / "market"
    _nodes_url = str(_api_url / "nodes")
    _edges_url = str(_api_url / "edges")
    _unlocked_url = str(_api_url / "unlocked")
    _shares_url = str(_api_url / "shares")
    _shares_all_url = str(_api_url / "shares" / "all")
    _demand_factors_url = str(_api_url / "demand_factors")

    @classmethod
    def get_markets(cls) -> list[Market]:
        """Get all markets (graph nodes).

        Returns:
            list[Market]: all market graph nodes.
        """
        response = httpx.get(cls._nodes_url, headers=st.session_state.auth_header)
        response.raise_for_status()
        return parse_obj_as(list[Market], response.json())

    @classmethod
    def get_edges(cls) -> list[tuple[int, int]]:
        """Get all markets edges.

        Returns:
            list[tuple[int, int]]: all market graph edges.
        """
        response = httpx.get(cls._edges_url, headers=st.session_state.auth_header)
        response.raise_for_status()
        return parse_obj_as(list[tuple[int, int]], response.json())

    @classmethod
    def get_unlocked_markets(cls) -> list[int]:
        """Get unlocked markets for particular user.

        Returns:
            list[int]: list of unlocked markets for the user.
        """
        response = httpx.get(cls._unlocked_url, headers=st.session_state.auth_header)
        response.raise_for_status()
        return parse_obj_as(list[int], response.json())

    @classmethod
    def get_shares_user(cls) -> list[MarketShare]:
        """Get market shares visible for user.

        Returns:
            list[MarketShare]: list of market shares.
        """
        response = httpx.get(cls._shares_url, headers=st.session_state.auth_header)
        response.raise_for_status()
        return parse_obj_as(list[MarketShare], response.json())

    @classmethod
    def get_shares(cls) -> list[MarketShare]:
        """Get market shares visible for user.

        Returns:
            list[MarketShare]: list of market shares.
        """
        response = httpx.get(cls._shares_all_url, headers=st.session_state.auth_header)
        response.raise_for_status()
        return parse_obj_as(list[MarketShare], response.json())

    @classmethod
    def get_demand_factors(cls) -> dict[int, float]:
        """Get demand factors for all markets.

        Returns:
            dict[int, float]: demand factors for all markets.
        """
        response = httpx.get(cls._demand_factors_url, headers=st.session_state.auth_header)
        response.raise_for_status()
        return parse_obj_as(dict[int, float], response.json())
