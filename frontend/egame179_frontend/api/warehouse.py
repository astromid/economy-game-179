"""Warehouse API."""
import httpx
import streamlit as st
from pydantic import BaseModel, parse_obj_as

from egame179_frontend.settings import settings


class Warehouse(BaseModel):
    """Warehouse model."""

    cycle: int
    user: int
    market: int
    quantity: int


class WarehouseAPI:
    """Warehouse API."""

    _api_url = settings.backend_url / "warehouse"
    _list_url = str(_api_url / "list")
    _list_all_url = str(_api_url / "list" / "all")

    @classmethod
    def get_user_storage(cls) -> list[Warehouse]:
        """Get current user storage.

        Returns:
            list[Warehouse]: current user storage.
        """
        response = httpx.get(cls._list_url, headers=st.session_state.auth_header)
        response.raise_for_status()
        return parse_obj_as(list[Warehouse], response.json())

    @classmethod
    def get_storages(cls) -> list[Warehouse]:
        """Get all users storage.

        Returns:
            list[Warehouse]: all users storage.
        """
        response = httpx.get(cls._list_all_url, headers=st.session_state.auth_header)
        response.raise_for_status()
        return parse_obj_as(list[Warehouse], response.json())
