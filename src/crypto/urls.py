from django.urls import path
from crypto.views import CryptoBalance,  CryptoAddTransactions, CryptoHistoryTransactions, persons_crypto


app_name = 'crypto'

crypto_patterns_api = [
    path('', CryptoBalance.as_view()),
    path('add/', CryptoAddTransactions.as_view()),
    path('history/', CryptoHistoryTransactions.as_view()),
    ]

crypto_patterns = [
    path('', persons_crypto, name='crypto'),

    ]