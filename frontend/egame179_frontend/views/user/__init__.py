"""User views."""
from egame179_frontend.views import View
from egame179_frontend.views.login import LOGOUT_OPTION
from egame179_frontend.views.user.manufacturing import manufacturing
from egame179_frontend.views.user.markets import markets
from egame179_frontend.views.user.overview import overview
from egame179_frontend.views.user.sales import sales
from egame179_frontend.views.user.stocks import stocks

USER_VIEWS = (
    View(menu_option="Статус", icon="house", page_func=overview),
    View(menu_option="Рынки", icon="pie-chart-fill", page_func=markets),
    View(menu_option="Производство", icon="gear", page_func=manufacturing),
    View(menu_option="Продажи", icon="receipt-cutoff", page_func=sales),
    View(menu_option="Акции", icon="graph-up", page_func=stocks),
    LOGOUT_OPTION,
)
