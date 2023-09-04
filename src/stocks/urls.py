from django.urls import path, include
from rest_framework import routers

from .views import StockViewSets, StockTransactions


router = routers.SimpleRouter()
router.register(r'stocks', StockViewSets)


stocks_patterns = [
    path('stocks/transactions/', StockTransactions.as_view()),
    path('', include(router.urls)),
]

from .apschedulers_tasks import *