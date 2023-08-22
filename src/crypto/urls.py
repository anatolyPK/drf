from django.urls import path
from crypto.views import CryptoBalance,  CryptoAddTransactions, CryptoHistoryTransactions

crypto_patterns = [
    path('', CryptoBalance.as_view()),
    path('add/', CryptoAddTransactions.as_view()),
    path('history/', CryptoHistoryTransactions.as_view()),
    ]