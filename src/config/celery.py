from __future__ import absolute_import, unicode_literals
import os

from celery import Celery
from celery.schedules import crontab

from config import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')
app.config_from_object('django.conf:settings', namespace="CELERY")
app.conf.broker_url = settings.CELERY_BROKER_URL
app.autodiscover_tasks()

app.conf.beat_schedule ={
    'fix_portfolio_balance': {
        'task': 'portfolio.tasks.fix_portfolio_balance',
        'schedule': crontab(minute='*/5')
    },

    'refresh_assets_from_tink_api': {
        'task': 'stocks.tasks.refresh_db_from_tinkoff_api',
        'schedule': crontab(hour='18', minute='48')
    },

    'delete_old_portfolio_balance': {
        'task': 'portfolio.tasks.delete_old_crypto_balance',
        'schedule': crontab(minute='*/10')
    },

    'update_cache_tickers_price': {
        'task': 'crypto.tasks.update_cache_tickers_price',
        'schedule': 30.0, #установить 10,0
    },

    'update_cache_stocks_price': {
        'task': 'stocks.tasks.update_cache_tickers_price',
        'schedule': 30.0, #установить 10,0
    },

    'update_coupons': {
        'task': 'stocks.tasks.refresh_coupons',
        'schedule': crontab(hour='18', minute='48'),
    }
}


