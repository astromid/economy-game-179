from dataclasses import dataclass
from typing import Callable

from egame179_frontend.views.login import logout
from egame179_frontend.views.root.dashboard import dashboard
from egame179_frontend.views.user.main_page import main_page


@dataclass
class View:
    """Contains information about a view."""

    menu_option: str
    icon: str
    page_func: Callable[[], None]


def get_root_views() -> list[View]:
    """Return a list of root views."""
    return [
        View(menu_option="Dashboard", icon="house", page_func=dashboard),
        View(menu_option="Exit", icon="box-arrow-right", page_func=logout),
    ]


def get_user_views() -> list[View]:
    """Return a list of user views."""
    return [
        View(menu_option="Main page", icon="house", page_func=main_page),
        View(menu_option="Exit", icon="box-arrow-right", page_func=logout),
    ]
