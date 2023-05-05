"""Prices API."""
import httpx
import streamlit as st
from pydantic import BaseModel, parse_obj_as

from egame179_frontend.settings import settings


class Price(BaseModel):
    """Price model."""

    cycle: int
    market_id: int
    buy: float
    sell: float


class PriceAPI:
    """Price API."""

    _all_prices_url = str(settings.backend_url / "price" / "all")

    @classmethod
    def get_market_prices(cls) -> list[Price]:
        """Get market prices.

        Returns:
            list[Prices]: prices for all markets.
        """
        response = httpx.get(cls._all_prices_url, headers=st.session_state.auth_header)
        response.raise_for_status()
        return parse_obj_as(list[Price], response.json())
