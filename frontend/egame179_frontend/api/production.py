"""Production API."""
from datetime import datetime

import httpx
import streamlit as st
from pydantic import BaseModel, parse_obj_as

from egame179_frontend.settings import settings


class Production(BaseModel):
    """Production order model."""

    id: int
    ts: datetime
    cycle: int
    user: int
    market: int
    quantity: int


class Theta(BaseModel):
    """Theta model"""

    cycle: int
    user: int
    market: int
    theta: float


class ProductionAPI:
    """Production API."""

    _api_url = settings.backend_url / "production"

    _user_products_url = str(_api_url / "list")
    _products_url = str(_api_url / "list" / "all")
    _user_thetas_url = str(_api_url / "thetas")
    _thetas_url = str(_api_url / "thetas" / "all")
    _new_url = str(_api_url / "new")

    @classmethod
    def get_user_products(cls) -> list[Production]:
        """Get current user production.

        Returns:
            list[Production]: current user production history.
        """
        response = httpx.get(cls._user_products_url, headers=st.session_state.auth_header)
        response.raise_for_status()
        return parse_obj_as(list[Production], response.json())

    @classmethod
    def get_products(cls) -> list[Production]:
        """Get all users products.

        Returns:
            list[Production]: all users product history.
        """
        response = httpx.get(cls._products_url, headers=st.session_state.auth_header)
        response.raise_for_status()
        return parse_obj_as(list[Production], response.json())

    @classmethod
    def get_user_thetas(cls) -> list[Theta]:
        response = httpx.get(cls._user_thetas_url, headers=st.session_state.auth_header)
        response.raise_for_status()
        return parse_obj_as(list[Theta], response.json())

    @classmethod
    def get_thetas(cls) -> list[Theta]:
        response = httpx.get(cls._thetas_url, headers=st.session_state.auth_header)
        response.raise_for_status()
        return parse_obj_as(list[Theta], response.json())

    @classmethod
    def new(cls, market: int, quantity: int) -> None:
        """Buy items on target market.

        Args:
            market (int): target market id.
            quantity (int): number of items.
        """
        bid = {"market": market, "quantity": quantity}
        response = httpx.post(cls._new_url, json=bid, headers=st.session_state.auth_header)
        response.raise_for_status()
