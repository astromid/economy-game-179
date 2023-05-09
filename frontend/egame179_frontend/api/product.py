"""Products API."""
import httpx
import streamlit as st
from pydantic import BaseModel, parse_obj_as

from egame179_frontend.settings import settings


class Product(BaseModel):
    """Product model."""

    cycle: int
    user_id: int
    market_id: int
    storage: int
    theta: float
    share: float


class MarketShare(BaseModel):
    """Market share model."""

    market_id: int
    user_id: int
    share: float | None = None
    position: int


class ProductAPI:
    """Product API."""

    _api_url = settings.backend_url / "product"

    _user_products_url = str(_api_url / "user")
    _all_products_url = str(_api_url / "all")
    _shares_url = str(_api_url / "shares")
    _buy_url = str(_api_url / "buy")

    @classmethod
    def get_user_products(cls) -> list[Product]:
        """Get current user products.

        Returns:
            list[Product]: current user product history.
        """
        response = httpx.get(cls._user_products_url, headers=st.session_state.auth_header)
        response.raise_for_status()
        return parse_obj_as(list[Product], response.json())

    @classmethod
    def get_products(cls) -> list[Product]:
        """Get all users products.

        Returns:
            list[Product]: all users product history.
        """
        response = httpx.get(cls._all_products_url, headers=st.session_state.auth_header)
        response.raise_for_status()
        return parse_obj_as(list[Product], response.json())

    @classmethod
    def get_shares(cls) -> list[MarketShare]:
        """Get market shares for previous cycle.

        Returns:
            list[MarketShare]: market shares (visible for current player).
        """
        response = httpx.get(cls._shares_url, headers=st.session_state.auth_header)
        response.raise_for_status()
        return parse_obj_as(list[MarketShare], response.json())

    @classmethod
    def buy(cls, market_id: int, amount: int) -> None:
        """Buy items on target market.

        Args:
            market_id (int): target market id.
            amount (int): number of items.
        """
        bid = {"market_id": market_id, "amount": amount}
        response = httpx.post(cls._buy_url, json=bid, headers=st.session_state.auth_header)
        response.raise_for_status()
