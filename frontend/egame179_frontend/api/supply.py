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
    user_id: int
    market_id: int
    declared_amount: int
    amount: int


class SupplyAPI:
    """Supply API."""

    _api_url = settings.backend_url / "supply"

    _user_supplies_url = str(_api_url / "user")
    _all_supplies_url = str(_api_url / "all")
    _make_supply_url = str(_api_url / "make")

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
        response = httpx.get(cls._all_supplies_url, headers=st.session_state.auth_header)
        response.raise_for_status()
        return parse_obj_as(list[Supply], response.json())

    @classmethod
    def make_supply(cls, market_id: int, amount: int) -> None:
        """Start supply to target market.

        Args:
            market_id (int): target market id.
            amount (int): number of items.
        """
        bid = {"market_id": market_id, "amount": amount}
        response = httpx.post(cls._make_supply_url, json=bid, headers=st.session_state.auth_header)
        response.raise_for_status()
