import logging
from typing import Literal, Union
from celery import shared_task
from django.contrib.auth.models import User

from crypto.binanceAPI import BinanceAPI, client
from portfolio.services.add_change_in_user_assets import AssetsChange
from django.core.cache import cache

logger = logging.getLogger('main')


@shared_task()
def update_cache_historical_klines():
    tickers = (pair['symbol'] for pair in BinanceAPI.get_all_tickers_prices())


@shared_task()
def update_cache_tickers_price():
    prices = BinanceAPI.get_all_tickers_prices()
    for price in prices:
        cache_name = price['symbol']
        current_price = float(price['price'])
        cache.set(cache_name, current_price, 30)


@shared_task()
def update_crypto_transaction(transaction):
    AssetsChange.change_crypto_transaction(transaction)


@shared_task()
def add_invest_sum_task(user_id: int,
                        invest_sum_in_usd: float or int,
                        invest_sum_in_rub: float or int,
                        date_operation: str):
    user = User.objects.get(pk=user_id)
    AssetsChange.add_invest_sum(assets_type='crypto',
                                invest_sum_in_rub=invest_sum_in_rub,
                                invest_sum_in_usd=invest_sum_in_usd,
                                date_operation=date_operation,
                                user=user)


@shared_task()
def add_transactions_and_update_users_portfolio(assets_type: Literal['crypto', 'stock'],
                                                is_buy_or_sell: Union[bool, int],
                                                lot: float,
                                                user_id: int,
                                                price_currency: float,
                                                currency: Literal['rub', 'usd', 'usdt'],
                                                date_operation=None,
                                                figi: str = None,
                                                token_1: str = None,
                                                token_2: str = None):
    user = User.objects.get(pk=user_id)
    AssetsChange.add_transaction_in_bd_and_update_users_assets(assets_type=assets_type,
                                                               is_buy_or_sell=is_buy_or_sell,
                                                               lot=lot,
                                                               user=user,
                                                               price_currency=price_currency,
                                                               currency=currency,
                                                               date_operation=date_operation,
                                                               token_1=token_1,
                                                               token_2=token_2,
                                                               figi=figi)
