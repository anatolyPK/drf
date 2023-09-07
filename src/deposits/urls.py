from django.urls import path, include
from rest_framework import routers

from .views import DepositsViewSets, DepositsTransactions, RegisterUser, persons_deposits

router = routers.SimpleRouter()
router.register(r'deposits', DepositsViewSets)


app_name = 'deposits'

deposits_patterns = [
    path('', persons_deposits, name='deposits'),
]

deposits_drf_patterns = [
    path('deposits/transaction/', DepositsTransactions.as_view()),
    path('', include(router.urls)),
]

from .apschedulers_tasks import *

