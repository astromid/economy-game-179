"""User views."""
from egame179_frontend.views.player.overview import PlayerDashboard

__all__ = ["PlayerDashboard"]

# from egame179_frontend.views.player.manufacturing import manufacturing_view
# from egame179_frontend.views.player.markets import markets_view
# from egame179_frontend.views.player.overview import overview
# from egame179_frontend.views.player.sales import sales_view
# from egame179_frontend.views.player.stocks import stocks_view
# from egame179_frontend.views.player.storage import storage_view
# from egame179_frontend.views.player.transactions import transactions_view

# USER_VIEWS = MappingProxyType(
#     {
#         "Статус": ("house", overview),
#         "Рынки": ("pie-chart-fill", markets_view),
#         "Производство": ("gear", manufacturing_view),
#         "Склад": ("box-seam", storage_view),
#         "Продажи": ("receipt-cutoff", sales_view),
#         "Акции": ("graph-up", stocks_view),
#         "Транзакции": ("cash-stack", transactions_view),
#     },
# )
