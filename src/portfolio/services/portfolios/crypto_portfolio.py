from portfolio.services.portfolios.base_portfolio import Portfolio
from typing import Tuple, Dict, List, Union
from django.contrib.auth.models import User
from django.core.cache import cache

import logging


logger = logging.getLogger('main')
logger_debug = logging.getLogger('debug')


class CryptoPortfolio(Portfolio):
    """
    Класс для работы с портфелем криптовалютных активов пользователя.
    """

    def __init__(self, user: User, assets):
        super().__init__(type_of_assets='crypto', user=user)
        self._make_portfolio(assets)

    # @staticmethod #нужно ли это...
    # def _get_user_assets(assets_type, user):  # пофиксить эту функцию . вверху есть подобная
    #     if assets_type == 'crypto':
    #         return PortfolioConfig.users_models[assets_type].objects.filter(user=user)
    #     elif assets_type == 'stock':
    #         return PortfolioConfig.users_models[assets_type]['share'].objects.filter(user=user)

    def _make_portfolio(self, user_assets):
        """
        Создает портфель криптовалютных активов пользователя.
        :param user_assets: активы пользователя
        :return:
        """
        try:
            logger_debug.debug(user_assets)
            self.current_usd_rub_price = cache.get('USDTRUB')
            for asset in user_assets:
                self._add_active_in_persons_portfolio(ident=asset.token,
                                                      lot=asset.lot,
                                                      average_price_buy_in_rub=asset.average_price_in_rub,
                                                      average_price_buy_in_usd=asset.average_price_in_usd,
                                                      current_price=self._get_current_price(asset),
                                                      currency='usd',
                                                      name=asset.token,
                                                      pk=asset.pk)
        except (AttributeError, KeyError) as ex:
            logger.warning(ex)

    @staticmethod
    def _get_current_price(asset):
        """
        Возвращает текущую цену криптовалютного актива.
        :param asset:
        :return:
        """
        try:
            if asset.token in ('usd', 'rub', 'usdc', 'usdt', 'busd'):
                return 1
            return cache.get(f'{asset.token.upper()}USDT')
        except (KeyError, AttributeError, TypeError) as ex:
            logger.warning(ex)


