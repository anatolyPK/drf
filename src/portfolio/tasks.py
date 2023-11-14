import logging
from typing import Literal, Union
from celery import shared_task
from django.contrib.auth.models import User

from portfolio.services.portfolio_balance import write_in_db_portfolio_balance, BalanceDeleter

logger = logging.getLogger('main')


@shared_task()
def fix_portfolio_balance():
    write_in_db_portfolio_balance()


#сделать и для stock deleter
@shared_task()
def delete_old_crypto_balance():
    BalanceDeleter.delete_old_balance()
