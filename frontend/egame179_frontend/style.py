import json
import logging
from enum import Enum
from pathlib import Path

import streamlit as st


class ThemeColors(Enum):
    """Theme colors."""

    RED = "#ee6666"  # noqa: WPS115
    GREEN = "#91cc75"  # noqa: WPS115
    BLUE = "#5470c6"  # noqa: WPS115
    GRAY = "#bbbbbb"  # noqa: WPS115
    AQUA = "#38aab0"  # noqa: WPS115


PlayerColors = ("#ee6666", "#91cc75", "#5470c6", "#bbbbbb", "#38aab0", "#da70d6")


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
