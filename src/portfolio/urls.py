from django.urls import path, include
from rest_framework import routers

from portfolio.views import UserPortfolio


app_name = 'portfolio'

portfolio_patterns = [
    path('', UserPortfolio.as_view(), name='portfolio'),
    # path('add/', add_stock_transaction, name='add_portfolio')
]
