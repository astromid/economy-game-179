"""Game administration views."""
from egame179_frontend.views import View
from egame179_frontend.views.login import LOGOUT_OPTION
from egame179_frontend.views.root.dashboard import dashboard

ROOT_VIEWS = (
    View(menu_option="Game status", icon="house", page_func=dashboard),
    LOGOUT_OPTION,
)
