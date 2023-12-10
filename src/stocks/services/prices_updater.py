from stocks.models import Share, Currency, Etf, Bond
from stocks.services.tinkoff_API import TinkoffAPI
from django.core.cache import cache

import logging


logger = logging.getLogger('main')
logger_debug = logging.getLogger('debug')


class PricesUpdater:
    @classmethod
    def update_assets_price(cls):
        assets_figis_list = cls._get_figis_all_assets()
        prices = TinkoffAPI.get_last_price_asset(figi=assets_figis_list)
        cls._set_prices_in_cache(prices)

    @classmethod
    def _set_prices_in_cache(cls, prices):
        for key, price in prices.items():
            cache.set(key, price, 300)

    @classmethod
    def _get_figis_all_assets(cls):
        figis = []
        for db in (Share, Bond, Currency, Etf):
            assets = db.objects.values("figi")
            assets_figi = cls._get_figi(assets)
            figis.extend(assets_figi)
        return figis

    @classmethod
    def _get_figi(cls, assets):
        return [asset['figi'] for asset in assets]

