from django.urls import path, include
from rest_framework import routers

from .views import StockViewSets, StockTransactions, PersonStock, PersonTransaction

router = routers.SimpleRouter()
router.register(r'stocks', StockViewSets)


stocks_patterns = [
    path('', PersonStock.as_view(), name='stocks'),
    path('add/', PersonTransaction.as_view(), name='add_stock')
]

stocks_patterns_api = [
    path('stocks/transactions/', StockTransactions.as_view()),
    path('', include(router.urls)),
]

from .apschedulers_tasks import *