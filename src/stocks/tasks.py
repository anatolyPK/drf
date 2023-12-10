import time
import logging
from typing import Literal, Union
from celery import shared_task
from celery.schedules import crontab
from config.celery import app
from portfolio.services.portfolio_balance import BalanceDeleter
from .services.prices_updater import PricesUpdater
from .services.refresh_bonds_shares_etfs_bd import TinkoffAssets


logger = logging.getLogger('main')


@shared_task()
def refresh_db_from_tinkoff_api():
    TinkoffAssets.update_all_assets()


@shared_task()
def refresh_coupons():
    TinkoffAssets.update_all_coupons()


@shared_task()
def update_cache_tickers_price():
    PricesUpdater.update_assets_price()
