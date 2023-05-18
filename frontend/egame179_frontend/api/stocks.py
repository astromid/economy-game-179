"""Stocks API."""
import httpx
import streamlit as st
from pydantic import BaseModel, parse_obj_as

from egame179_frontend.settings import settings


class Stock(BaseModel):
    """Stock model."""

    cycle: int
    user: int
    price: float


class StocksAPI:
    """Balance API."""

    _api_url = str(settings.backend_url / "stocks/list")

    @classmethod
    def get_stocks(cls) -> list[Stock]:
        """Get stocks.

        Returns:
            list[Stock]: stocks price history.
        """
        response = httpx.get(cls._api_url, headers=st.session_state.auth_header)
        response.raise_for_status()
        return parse_obj_as(list[Stock], response.json())
