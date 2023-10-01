import logging
from typing import Literal, Union
from celery import shared_task
from django.contrib.auth.models import User

from portfolio.services.add_change_in_user_assets import AssetsChange


logger = logging.getLogger('main')


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
