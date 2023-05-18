"""Sync status API."""
import httpx
import streamlit as st
from pydantic import parse_obj_as

from egame179_frontend.settings import settings


class SyncStatusAPI:
    """Sync status API."""

    _api_url = settings.backend_url
    _sync_url = str(_api_url / "sync")
    _status_url = str(_api_url / "sync" / "status")

    @classmethod
    def sync(cls) -> None:
        """Send sync signal."""
        response = httpx.get(cls._status_url, headers=st.session_state.auth_header)
        response.raise_for_status()

    @classmethod
    def get_sync_status(cls) -> dict[int, bool]:
        """Get users sync status.

        Returns:
            dict[int, bool]: users sync status.
        """
        response = httpx.get(cls._status_url, headers=st.session_state.auth_header)
        response.raise_for_status()
        return parse_obj_as(dict[int, bool], response.json())
