"""Module with streamlit application views."""
from collections.abc import Callable
from dataclasses import dataclass

from egame179_frontend.api.models import PlayerState


@dataclass
class View:
    """Contains information about a view."""

    menu_option: str
    icon: str
    page_func: Callable[[PlayerState], None]
