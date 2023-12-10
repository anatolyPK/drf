from django.core.cache import cache
from django.contrib.auth.models import User

import logging

from portfolio.services.portfolios.base_portfolio import Portfolio, PersonsPortfolioDB
from stocks.models import UserShare
from stocks.services.tinkoff_API import TinkoffAPI

logger = logging.getLogger('main')
logger_debug = logging.getLogger('debug')


class StockPortfolio(Portfolio):
    def __init__(self, user: User, assets):
        super().__init__(type_of_assets='stock', user=user)
        self._make_portfolio(assets)

        # self._shares_price = 0
        # self._bonds_price = 0
        # self._currencies_price = 0
        # self._etfs_price = 0
        #
        # self._set_assets_prices()

    def _make_portfolio(self, assets_list):
        self.current_usd_rub_price = cache.get('USDTRUB')

        try:
            if all(isinstance(asset, UserShare) for asset in assets_list):
                user_bond, user_currency, user_etf = self._get_other_users_assets()
                for group_asset in (assets_list, user_bond, user_currency, user_etf):
                    for asset in group_asset:
                        self._add_active_in_persons_portfolio(
                            ident=asset.figi.figi,
                            lot=asset.lot,
                            average_price_buy_in_rub=asset.average_price_in_rub,
                            average_price_buy_in_usd=asset.average_price_in_usd,
                            current_price=self._get_current_price(asset.figi.figi),
                            currency=asset.figi.currency,
                            name=asset.figi.name,
                            pk=asset.pk,
                            stock_tag=group_asset.model._meta.model_name,
                            asset_typ=asset.figi,
                        )
                        logger_debug.debug('ADD')
        except (AttributeError, KeyError) as ex:
            logger.warning(ex)

    def _get_other_users_assets(self):
        return (
            PersonsPortfolioDB._get_users_assets_from_model(user=self.user, type_of_assets='stock',
                                                            assets=type_of_assets)
            for type_of_assets in ('bond', 'currency', 'etf')
        )

    @staticmethod
    def _get_current_price(figi):
        """
        Возвращает текущую цену актива.
        :param figi:
        :return:
        """
        try:
            return cache.get(figi)
        except (KeyError, AttributeError, TypeError) as ex:
            logger.warning(ex)

    # def _set_assets_prices(self):
    #     _share_prices = 0
    #     _bond_prices = 0
    #     _etf_prices = 0
    #     _currency_prices = 0
    #
    #     models = {
    #         'usershare': 0,
    #         'userbond': 0,
    #         'useretf': 0,
    #         'usercurrency': 0,
    #     }
    #
    #     for asset in self.assets.values():
    #         models[asset._stock_tag] += asset._total_now_balance_in_rub
    #
    #     logger_debug.debug(models)