"""Users auth API."""
from enum import Enum

import httpx
import streamlit as st
from pydantic import BaseModel, parse_obj_as

from egame179_frontend.settings import settings


class UserRoles(Enum):
    """User roles."""

    ROOT = "root"  # noqa: WPS115
    NEWS = "news"  # noqa: WPS115
    PLAYER = "player"  # noqa: WPS115


class User(BaseModel):
    """User model."""

    id: int
    role: str
    name: str


class AuthAPI:
    """Authentication API."""

    _token_url = str(settings.backend_url / "token")
    _user_url = str(settings.backend_url / "user")
    _names_url = str(settings.backend_url / "names")
    _players_url = str(settings.backend_url / "players")

    @classmethod
    def get_auth_header(cls, login: str, password: str) -> dict[str, str] | None:
        """Get authentication header for the given login and password.

        Args:
            login (str): user login.
            password (str): user password.

        Returns:
            dict[str, str] | None: auth header or None if login or password is incorrect.
        """
        response = httpx.post(cls._token_url, data={"username": login, "password": password})
        if response.status_code == httpx.codes.UNAUTHORIZED:
            return None
        token_data = response.json()
        return {"Authorization": f"Bearer {token_data['access_token']}"}

    @classmethod
    def get_user(cls, auth_header: dict[str, str]) -> User | None:
        """Get authenticated user info.

        Args:
            auth_header (dict[str, str]): auth header.

        Returns:
            User | None: user info or None if auth header is incorrect.
        """
        response = httpx.get(cls._user_url, headers=auth_header)
        if response.status_code == httpx.codes.UNAUTHORIZED:
            return None
        return User.parse_obj(response.json())

    @classmethod
    def get_names(cls) -> dict[int, str]:
        """Get player names mapping.

        Returns:
            dict[int, str]: {user: name} mapping.
        """
        response = httpx.get(cls._names_url, headers=st.session_state.auth_header)
        response.raise_for_status()
        return parse_obj_as(dict[int, str], response.json())

    @classmethod
    def get_players(cls) -> list[int]:
        """Get player ids.

        Returns:
            list[int]: player ids.
        """
        response = httpx.get(cls._names_url, headers=st.session_state.auth_header)
        response.raise_for_status()
        return parse_obj_as(list[int], response.json())
