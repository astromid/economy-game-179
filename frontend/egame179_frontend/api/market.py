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
    link1: int
    link2: int
    link3: int
    link4: int | None
    link5: int | None


class UnlockedMarket(BaseModel):
    """Unlocked market model."""

    user_id: int
    market_id: int
    protected: bool


class MarketAPI:
    """Market API."""

    all_markets_url = str(settings.backend_url / "market/all")
    user_unlocked_markets_url = str(settings.backend_url / "market/unlocked/user")
    all_unlocked_markets_url = str(settings.backend_url / "market/unlocked/all")

    @classmethod
    def get_markets(cls) -> list[Market]:
        """Get all markets (graph nodes).

        Returns:
            list[Market]: all market graph nodes.
        """
        response = httpx.get(cls.all_markets_url, headers=st.session_state.auth_header)
        response.raise_for_status()
        return parse_obj_as(list[Market], response.json())

    @classmethod
    def get_user_unlocked_markets(cls) -> list[UnlockedMarket]:
        """Get unlocked markets for particular user.

        Returns:
            list[UnlockedMarket]: list of unlocked markets for the user.
        """
        response = httpx.get(cls.user_unlocked_markets_url, headers=st.session_state.auth_header)
        response.raise_for_status()
        return parse_obj_as(list[UnlockedMarket], response.json())

    @classmethod
    def get_unlocked_markets(cls) -> list[UnlockedMarket]:
        """Get unlocked markets for all users.

        Returns:
            list[UnlockedMarket]: list of unlocked markets.
        """
        response = httpx.get(cls.all_unlocked_markets_url, headers=st.session_state.auth_header)
        response.raise_for_status()
        return parse_obj_as(list[UnlockedMarket], response.json())
