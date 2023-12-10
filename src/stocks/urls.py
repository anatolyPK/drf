from django.urls import path, include
from rest_framework import routers

from .views import PersonStock, add_stock_transaction, calculate_bond, PersonStockPortfolio, add_portfolio, \
    PersonStockTransaction, PersonStockTransactionEdit

router = routers.SimpleRouter()
# router.register(r'stocks', StockViewSets)


stocks_patterns = [
    path('', PersonStock.as_view(), name='stocks'),
    path('add/', add_stock_transaction, name='add_stock'),
    path('bonds_calc/', calculate_bond, name='bonds_calcul'),
    path('portfolio/<int:portfolio_id>/', PersonStock.as_view(), name='stock_portfolio'),
    path('add_portfolio/', add_portfolio, name='add_portfolio'),
    path('transactions/<slug:assets_type>/', PersonStockTransaction.as_view(), name='transactions'),
    path('transactions/<slug:assets_type>/<int:pk>', PersonStockTransactionEdit.as_view(),
         name='transaction_edit'),
    ]

stocks_patterns_api = [
    # path('stocks/transactions/', StockTransactions.as_view()),
    path('', include(router.urls)),
]

