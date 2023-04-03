import json
import logging
from pathlib import Path

import streamlit as st


def load_css() -> None:
    """Load CSS styles."""
    log = logging.getLogger(__name__)
    styles_dir = Path(__file__).parent.parent / "css"
    main_style = _load_main_style(styles_dir)
    log.debug("CSS files loaded")
    st.markdown(f"<style>{main_style}</style>", unsafe_allow_html=True)


@st.cache_resource
def _load_main_style(styles_dir: Path) -> str:
    return styles_dir.joinpath("style.css").read_text()


@st.cache_resource
def _load_menu_style(styles_dir: Path) -> dict:
    return json.loads(styles_dir.joinpath("menu.css.json").read_text())
