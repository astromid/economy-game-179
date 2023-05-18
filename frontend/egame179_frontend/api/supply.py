"""Products API."""
from datetime import datetime

import httpx
import streamlit as st
from pydantic import BaseModel, parse_obj_as

from egame179_frontend.settings import settings


class Supply(BaseModel):
    """Supply model."""

    id: int
    ts_start: datetime
    ts_finish: datetime | None = None
    cycle: int
    user: int
    market: int
    quantity: int
    delivered: int


class SupplyAPI:
    """Supply API."""

    _api_url = settings.backend_url / "supply"

    _user_supplies_url = str(_api_url / "list")
    _supplies_url = str(_api_url / "list/all")
    _new_url = str(_api_url / "new")

    @classmethod
    def get_user_supplies(cls) -> list[Supply]:
        """Get current user supplies.

        Returns:
            list[Supply]: current user supplies.
        """
        response = httpx.get(cls._user_supplies_url, headers=st.session_state.auth_header)
        response.raise_for_status()
        return parse_obj_as(list[Supply], response.json())

    @classmethod
    def get_supplies(cls) -> list[Supply]:
        """Get all users supplies.

        Returns:
            list[Supply]: all users supplies.
        """
        response = httpx.get(cls._supplies_url, headers=st.session_state.auth_header)
        response.raise_for_status()
        return parse_obj_as(list[Supply], response.json())

    @classmethod
    def new(cls, market: int, quantity: int) -> None:
        """Start supply to target market.

        Args:
            market (int): target market id.
            quantity (int): number of items.
        """
        bid = {"market": market, "quantity": quantity}
        response = httpx.post(cls._new_url, json=bid, headers=st.session_state.auth_header)
        response.raise_for_status()
