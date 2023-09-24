from django.urls import path
from crypto.views import CryptoBalance, CryptoAddTransactions, CryptoHistoryTransactions, CryptoPersonBalance, \
    add_transaction, add_invest_sum, PersonCryptoEdit, PersonCryptoTransaction, PersonCryptoTransactionEdit

app_name = 'crypto'

crypto_patterns_api = [
    path('', CryptoBalance.as_view(), name='crypto'),
    path('add/', CryptoAddTransactions.as_view(), name='add_crypto'),
    path('history/', CryptoHistoryTransactions.as_view()),
    ]

crypto_patterns = [
    path('', CryptoPersonBalance.as_view(), name='crypto'),
    path('<int:pk>/', PersonCryptoEdit.as_view(), name='person_crypto_edit'),

    path('transactions/', PersonCryptoTransaction.as_view(), name='person_crypto_transactions'),
    path('transactions/<int:pk>/', PersonCryptoTransactionEdit.as_view(), name='person_crypto_transaction_edit'),

    path('add_crypto/', add_transaction, name='add_crypto'),
    path('add_invest/', add_invest_sum, name='add_invest')
    ]