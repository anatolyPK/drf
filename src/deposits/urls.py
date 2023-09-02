from django.urls import path, include
from rest_framework import routers

from .views import DepositsViewSets, DepositsTransactions


router = routers.SimpleRouter()
router.register(r'deposits', DepositsViewSets)


deposits_patterns = [
    path('deposits/transaction/', DepositsTransactions.as_view()),
    path('', include(router.urls)),
]


