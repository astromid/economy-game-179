import json
from pathlib import Path

import streamlit as st
from streamlit_server_state import server_state, server_state_lock

STYLES_DIR = Path(__file__).parent.parent / "css"


def load_css() -> None:
    """Load CSS styles."""
    main_style = server_state.get("style", None)
    menu_style = server_state.get("menu_style", None)

    if main_style is None:
        main_style = STYLES_DIR.joinpath("style.css").read_text()
        with server_state_lock["style"]:
            server_state["style"] = main_style

    if menu_style is None:
        menu_style = json.loads(STYLES_DIR.joinpath("menu.json").read_text())
        with server_state_lock["menu_style"]:
            server_state["menu_style"] = menu_style

    st.markdown(f"<style>{server_state.style}</style>", unsafe_allow_html=True)
