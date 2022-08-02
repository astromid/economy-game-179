from pathlib import Path

import streamlit as st
import ujson

from egame179_frontend.api.models import PlayerState


@st.experimental_memo
def mock_player_state() -> PlayerState:
    json_string = Path("frontend/egame179_frontend/api/player_mock.json").read_text()
    return PlayerState.parse_obj(ujson.loads(json_string))


def mock_auth(login: str, password: str) -> str | None:
    if login == "corp" and password == "123":
        return "AQIDBAUGBwgJCgsMDQ4PEA=="


def mock_check_token(token: str | None) -> str | None:
    if token == "AQIDBAUGBwgJCgsMDQ4PEA==":
        return "corp"
