"""Balances API."""
import httpx
import streamlit as st
from pydantic import BaseModel, parse_obj_as

from egame179_frontend.settings import settings


class Balance(BaseModel):
    """Balance model."""

    cycle: int
    user_id: int
    amount: float


class BalanceAPI:
    """Balance API."""
    _api_url = settings.backend_url / "balance"

    _user_balances_url = str(_api_url / "user")
    _all_balances_url = str(_api_url / "all")

    @classmethod
    def get_user_balances(cls) -> list[Balance]:
        """Get current user balances.

        Returns:
            list[Balance]: current user balance history.
        """
        response = httpx.get(cls._user_balances_url, headers=st.session_state.auth_header)
        response.raise_for_status()
        return parse_obj_as(list[Balance], response.json())

    @classmethod
    def get_all_balances(cls) -> list[Balance]:
        """Get all users balances.

        Returns:
            list[Balance]: all users balance history.
        """
        response = httpx.get(cls._all_balances_url, headers=st.session_state.auth_header)
        response.raise_for_status()
        return parse_obj_as(list[Balance], response.json())
