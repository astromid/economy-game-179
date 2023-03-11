import json
import logging
from pathlib import Path

import streamlit as st
from streamlit_server_state import server_state, server_state_lock


def load_css() -> None:
    """Load CSS styles."""
    log = logging.getLogger(__name__)
    styles_dir = Path(__file__).parent.parent / "css"

    main_style = server_state.get("style", None)
    menu_style = server_state.get("menu_style", None)

    if main_style is None:
        main_style = styles_dir.joinpath("style.css").read_text()
        with server_state_lock["style"]:
            server_state["style"] = main_style
        log.debug("style.css loaded")

    if menu_style is None:
        menu_style = json.loads(styles_dir.joinpath("menu.css.json").read_text())
        with server_state_lock["menu_style"]:
            server_state["menu_style"] = menu_style
        log.debug("menu.css loaded")

    st.markdown(f"<style>{server_state.style}</style>", unsafe_allow_html=True)
