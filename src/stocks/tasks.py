import time
import logging
from typing import Literal, Union
from celery import shared_task
from celery.schedules import crontab
from config.celery import app
from .services.refresh_bonds_shares_etfs_bd import TinkoffAssets


logger = logging.getLogger('main')


@shared_task()
def refresh_db_from_tinkoff_api():
    TinkoffAssets.update_all_assets()


