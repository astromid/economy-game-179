"""User views."""
from egame179_frontend.views import View
from egame179_frontend.views.login import LOGOUT_OPTION
from egame179_frontend.views.user.manufacturing import manufacturing_view
from egame179_frontend.views.user.markets import markets_view
from egame179_frontend.views.user.overview import overview
from egame179_frontend.views.user.sales import sales_view
from egame179_frontend.views.user.stocks import stocks_view
from egame179_frontend.views.user.storage import storage_view
from egame179_frontend.views.user.transactions import transactions_view

USER_VIEWS = (
    View(menu_option="Статус", icon="house", page_func=overview),
    View(menu_option="Рынки", icon="pie-chart-fill", page_func=markets_view),
    View(menu_option="Производство", icon="gear", page_func=manufacturing_view),
    View(menu_option="Склад", icon="box-seam", page_func=storage_view),
    View(menu_option="Продажи", icon="receipt-cutoff", page_func=sales_view),
    View(menu_option="Акции", icon="graph-up", page_func=stocks_view),
    View(menu_option="Транзакции", icon="cash-stack", page_func=transactions_view),
    LOGOUT_OPTION,
)
