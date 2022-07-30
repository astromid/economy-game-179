from dataclasses import dataclass
from typing import Callable

from egame179_frontend.views.login import logout
from egame179_frontend.views.root.dashboard import dashboard
from egame179_frontend.views.user.main_page import main_page


@dataclass
class View:
    menu_option: str
    icon: str
    page_func: Callable[[], None]


EXIT_OPTION = View(menu_option="Exit", icon="box-arrow-right", page_func=logout)
USER_VIEWS = (
    View(menu_option="Main page", icon="gear", page_func=main_page),
    EXIT_OPTION,
)
ROOT_VIEWS = (
    View(menu_option="Dashboard", icon="house", page_func=dashboard),
    EXIT_OPTION,
)
