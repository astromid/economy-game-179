"""Balances API."""
import httpx
import streamlit as st
from pydantic import BaseModel, parse_obj_as

from egame179_frontend.settings import settings


class Balance(BaseModel):
    """Balance model."""

    cycle: int
    user: int
    balance: float


class BalanceAPI:
    """Balance API."""

    _api_url = settings.backend_url / "balance"
    _list_url = str(_api_url / "list")
    _list_all_url = str(_api_url / "list" / "all")

    @classmethod
    def get_user_balances(cls) -> list[Balance]:
        """Get current user balances.

        Returns:
            list[Balance]: current user balance history.
        """
        response = httpx.get(cls._list_url, headers=st.session_state.auth_header)
        response.raise_for_status()
        return parse_obj_as(list[Balance], response.json())

    @classmethod
    def get_balances(cls) -> list[Balance]:
        """Get all users balances.

        Returns:
            list[Balance]: all users balance history.
        """
        response = httpx.get(cls._list_all_url, headers=st.session_state.auth_header)
        response.raise_for_status()
        return parse_obj_as(list[Balance], response.json())
