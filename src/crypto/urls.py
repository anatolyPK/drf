from django.urls import path
from crypto.views import CryptoBalance, CryptoAddTransactions, CryptoHistoryTransactions, CryptoPersonBalance, \
    add_transaction, add_invest_sum

app_name = 'crypto'

crypto_patterns_api = [
    path('', CryptoBalance.as_view(), name='crypto'),
    path('add/', CryptoAddTransactions.as_view(), name='add_crypto'),
    path('history/', CryptoHistoryTransactions.as_view()),
    ]

crypto_patterns = [
    path('', CryptoPersonBalance.as_view(), name='crypto'),
    path('add_crypto/', add_transaction, name='add_crypto'),
    path('add_invest/', add_invest_sum, name='add_invest')
    ]