from typing import Tuple, Dict, List, Union, Literal

from django.contrib.auth.models import User

from .portfolios import CryptoPortfolio, StockPortfolio
from .config import PortfolioConfig, Crypto, Stock

import logging


logger = logging.getLogger('main')
logger_debug = logging.getLogger('debug')


class PortfolioMaker:
    def __init__(self, assets_type: Union[type(Crypto), type(Stock)], user: User, assets=None, is_portfolio: bool = False):
        portfolio_class = self._get_assets_class(assets_type)

        self.portfolio = portfolio_class(user=user, assets=assets)

    @staticmethod
    def _get_assets_class(assets_type):
        assets_classes = {
            Crypto: CryptoPortfolio,
            Stock: StockPortfolio
        }
        if assets_type not in assets_classes:
            raise ValueError(f"Unsupported assets_type: {assets_type}")
        return assets_classes[assets_type]

# //TODO сделать чтообы актив не отображался если маленький баланс
