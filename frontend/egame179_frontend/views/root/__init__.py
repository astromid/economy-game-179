"""Game administration views."""
from egame179_frontend.views import View
from egame179_frontend.views.root.dashboard import dashboard

ROOT_VIEWS = (View(menu_option="Статус", icon="house", page_func=dashboard),)
