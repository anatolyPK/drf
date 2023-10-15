from typing import Tuple, Dict, List, Union

from django.contrib.auth.models import User
from django.db.models import Sum

from crypto.binanceAPI import BinanceAPI
from crypto.models import PersonsCrypto
from stocks.models import UserStock
from .config import PortfolioConfig
from .arithmetics import ArithmeticOperations
from stocks.services.tinkoff_API import TinkoffAPI

import logging


logger = logging.getLogger('main')
logger_debug = logging.getLogger('debug')


class AssetsInfo(PortfolioConfig):
    """Класс, хранящий информацию о конкретном активе"""

    def __init__(self, **kwargs):
        """
        :param kwargs:
            ident (str): Уникальный идентификатор актива.
            name (str): Название актива.
            lot (float): Количество актива.
            average_price_buy_in_rub (float): Средняя цена покупки в рублях.
            average_price_buy_in_usd (float): Средняя цена покупки в долларах.
            current_price (float): Текущая цена актива.
            usd_rub_currency (float): Курс USD к RUB.
            currency (str): Валюта актива.
            pk (int): Primary Key актива в базе данных.
        """
        try:
            self.ident = kwargs['ident']
            self.name = kwargs['name']
            self.lot = kwargs['lot']
            self.average_price_buy_in_rub = kwargs['average_price_buy_in_rub']
            self.average_price_buy_in_usd = kwargs['average_price_buy_in_usd']
            self.current_price = kwargs['current_price']
            self.usd_rub_currency = kwargs['usd_rub_currency']
            self.currency = kwargs['currency']
            self.pk = kwargs['pk']

            self.total_now_balance_in_rub, self.total_now_balance_in_usd = \
                ArithmeticOperations.count_rub_and_usd_price(currency=self.currency,
                                                             current_price=self.current_price,
                                                             lot=self.lot,
                                                             usd_rub_currency=self.usd_rub_currency)
            self._count_profits_in_currencies()
            self._count_profits_in_percents()

        except KeyError as ex:
            logger.warning((kwargs, ex))

    def _count_profits_in_percents(self) -> None:
        """Вычисляет прибыль актива в процентах (в рублях и долларах)"""
        self.profit_in_percent_rub = ArithmeticOperations.count_percent_profit(self.average_price_buy_in_rub * self.lot,
                                                                               self.total_now_balance_in_rub)
        self.profit_in_percent_usd = ArithmeticOperations.count_percent_profit(self.average_price_buy_in_usd * self.lot,
                                                                               self.total_now_balance_in_usd)

    def _count_profits_in_currencies(self) -> None:
        """Вычисляет прибыль актива в валюте (в рублях и долларах)"""
        try:
            self.profit_in_currency_rub = self.total_now_balance_in_rub - self.average_price_buy_in_rub * self.lot
            self.profit_in_currency_usd = self.total_now_balance_in_usd - self.average_price_buy_in_usd * self.lot
        except TypeError as ex:
            logger.warning(ex)


class PortfolioBalance(PortfolioConfig):
    def __init__(self, user, type_of_assets, *args, **kwargs):
        self._current_usd_rub_price = 0
        self._buy_price_in_rub = 0
        self._buy_price_in_usd = 0
        self._total_balance_in_rub = 0
        self._total_balance_in_usd = 0
        self._type_of_assets = type_of_assets
        self._user = user

    def _add_price_in_total_and_buy_balance(self, **kwargs) -> None:
        self._add_price_in_total_balance(**kwargs)
        self._add_price_in_buy_price(**kwargs)

    def _add_price_in_total_balance(self, **kwargs):
        price_in_rub, price_in_usd = ArithmeticOperations.count_rub_and_usd_price(currency=kwargs['currency'],
                                                                                  current_price=kwargs['current_price'],
                                                                                  lot=kwargs['lot'],
                                                                                  usd_rub_currency=self._current_usd_rub_price)
        self._total_balance_in_rub += price_in_rub
        self._total_balance_in_usd += price_in_usd

    def _add_price_in_buy_price(self, **kwargs):
        try:
            self._buy_price_in_rub += kwargs['average_price_buy_in_rub'] * kwargs['lot']
            self._buy_price_in_usd += kwargs['average_price_buy_in_usd'] * kwargs['lot']
        except (KeyError, TypeError) as ex:
            logger.warning((kwargs, ex))


class PersonsPortfolioDB(PortfolioBalance):
    def _get_users_assets_from_model(self):
        """
        Возвращает активы пользователя на основе модели соответствующего типа.
        """
        try:
            return self.users_models[self._type_of_assets].objects.filter(user=self._user)
        except (KeyError, ValueError) as ex:
            logger.warning(ex)
            return None

    def _get_currencies_and_names_from_bd(self, figis: list) -> Tuple[Dict[str, str], Dict[str, str]]:
        """
        Возвращает словари валют и имен активов на основе списка FIGI.
        """
        currencies, names = {}, {}
        try:
            for model_class in self._models_for_shares_bonds_etfs_currencies.values():
                assets_from_bd = model_class.objects.filter(figi__in=figis)
                for asset in assets_from_bd:
                    currencies[asset.figi] = asset.currency
                    names[asset.figi] = asset.name
        except ValueError as ex:
            logger.warning(f"Error: {ex}, FIGIs: {figis}")
        return currencies, names

    def get_invest_sum(self) -> Tuple[float, float]:
        """
        Возвращает сумму инвестирования в формате (сумма в рублях, сумма в долларах).
        Если нет записей - возвращает: (0, 0), (0, 1)
        """
        invest_sum_dict = (self._users_invest_sum_models[self._type_of_assets].objects.filter(user=self._user).
                           aggregate(invest_sum_in_rub=Sum('invest_sum_in_rub'),
                                     invest_sum_in_usd=Sum('invest_sum_in_usd')))

        invest_sum_rub = invest_sum_dict.get('invest_sum_in_rub', 0) or 0
        invest_sum_usd = invest_sum_dict.get('invest_sum_in_usd', 0) or 0
        logger_debug.debug(f'{invest_sum_dict} {invest_sum_rub} {invest_sum_usd}')

        return invest_sum_rub, invest_sum_usd


class Portfolio(PersonsPortfolioDB, ArithmeticOperations):
    """Класс для работы с портфелем пользователя."""

    def __init__(self, *, type_of_assets: str, user):
        super().__init__(type_of_assets=type_of_assets,
                         user=user)
        self._tickers = {}
        self.invest_sum_in_rub, self.invest_sum_in_usd = self.get_invest_sum()
        logger_debug.debug(self.get_invest_sum())

    def _add_active_in_persons_portfolio(self, **kwargs):
        """Добавление актива в портфель"""
        self._add_price_in_total_and_buy_balance(**kwargs)
        try:
            self._tickers[kwargs['ident']] = AssetsInfo(usd_rub_currency=self._current_usd_rub_price, **kwargs)
        except KeyError as ex:
            logger.warning((kwargs, ex))

    def get_info_about_portfolio_and_assets(self) -> dict:
        """Возвращает информацию о портфеле, а также об активах."""
        portfolios_info = self.get_info_about_portfolio()
        portfolios_info['assets'] = self.get_info_about_assets()

        return portfolios_info

    def get_info_about_portfolio(self) -> dict:
        """Возвращает информацию о портфеле"""
        params_dict = {'total_balance_in_rub': ArithmeticOperations.round_number(self._total_balance_in_rub),
                       'total_balance_in_usd': ArithmeticOperations.round_number(self._total_balance_in_usd),
                       'buy_price_in_rub': ArithmeticOperations.round_number(self._buy_price_in_rub),
                       'buy_price_in_usd': ArithmeticOperations.round_number(self._buy_price_in_usd),
                       'profit_in_percents_rub':
                           ArithmeticOperations.round_number(self.count_percent_profit(self._buy_price_in_rub,
                                                                                       self._total_balance_in_rub)),
                       'profit_in_percents_usd':
                           ArithmeticOperations.round_number(self.count_percent_profit(self._buy_price_in_usd,
                                                                                       self._total_balance_in_usd)),
                       'profit_in_currency_rub':
                           ArithmeticOperations.round_number(self._total_balance_in_rub - self._buy_price_in_rub),
                       'profit_in_currency_usd':
                           ArithmeticOperations.round_number(self._total_balance_in_usd - self._buy_price_in_usd),
                       'usd_rub_currency': ArithmeticOperations.round_number(self._current_usd_rub_price),
                       'profit_invest_in_rub_in_percent':
                           ArithmeticOperations.round_number(self.count_percent_profit(self.invest_sum_in_rub,
                                                                                       self._total_balance_in_rub)),
                       'profit_invest_in_usd_in_percent':
                           ArithmeticOperations.round_number(self.count_percent_profit(self.invest_sum_in_usd,
                                                                                       self._total_balance_in_usd)),
                       'profit_invest_in_rub_in_currency':
                           ArithmeticOperations.round_number(self._total_balance_in_rub - self.invest_sum_in_rub),
                       'profit_invest_in_usd_in_currency':
                           ArithmeticOperations.round_number(self._total_balance_in_usd - self.invest_sum_in_usd),
                       'invest_sum_in_rub': ArithmeticOperations.round_number(self.invest_sum_in_rub),
                       'invest_sum_in_usd': ArithmeticOperations.round_number(self.invest_sum_in_usd),
                       }
        return params_dict

    def get_info_about_assets(self) -> dict:
        """Возвращает информацию об активах. Возвращает словарь активов, отсортированных по доле в портфеле
        (от самого большого)"""
        tickers_info = {}

        for ticker, info in self._tickers.items():
            tickers_info[ticker] = {
                'name': info.name,
                'lot': ArithmeticOperations.round_number(info.lot, self.ROUND_DIGIT_LOT),
                'average_price_buy_in_rub': ArithmeticOperations.round_number(info.average_price_buy_in_rub),
                'average_price_buy_in_usd': ArithmeticOperations.round_number(info.average_price_buy_in_usd),
                'current_price': ArithmeticOperations.round_number(info.current_price),
                'currency': self._get_currency_symbol(info.currency),
                'profit_in_currency_rub': ArithmeticOperations.round_number(info.profit_in_currency_rub),
                'profit_in_currency_usd': ArithmeticOperations.round_number(info.profit_in_currency_usd),
                'profit_in_percent_rub': ArithmeticOperations.round_number(info.profit_in_percent_rub),
                'profit_in_percent_usd': ArithmeticOperations.round_number(info.profit_in_percent_usd),
                'total_now_balance_in_rub': ArithmeticOperations.round_number(info.total_now_balance_in_rub),
                'total_now_balance_in_usd': ArithmeticOperations.round_number(info.total_now_balance_in_usd),
                'profit_in_currency': ArithmeticOperations.round_number(info.profit_in_currency_usd),
                'profit_in_percent': ArithmeticOperations.round_number(info.profit_in_percent_usd),
                'total_now_balance': ArithmeticOperations.round_number(info.total_now_balance_in_usd),
                'percent_of_portfolio':
                    ArithmeticOperations.round_number(ArithmeticOperations.count_percent(info.total_now_balance_in_usd,
                                                                                         self._total_balance_in_usd)),
                'pk': info.pk,
            }

        return dict(sorted(tickers_info.items(), key=lambda item: item[1]['percent_of_portfolio'], reverse=True))

    def _get_currency_symbol(self, currency: str) -> str:
        if currency.lower() in ('usd', 'usdt'):
            return '$'
        elif currency.lower() == 'rub':
            return '₽'


class CryptoPortfolio(Portfolio):
    """
    Класс для работы с портфелем криптовалютных активов пользователя.
    """

    def __init__(self, user: User, assets: List[PersonsCrypto]):
        super().__init__(type_of_assets='crypto', user=user)
        self._make_portfolio(assets)

    def _make_portfolio(self, user_assets):
        """
        Создает портфель криптовалютных активов пользователя.
        :param user_assets: активы пользователя
        :return:
        """
        try:
            tokens = self._get_tokens_for_binance_api(user_assets)
            current_prices_of_assets = BinanceAPI.get_tickers_prices(tokens)

            self._current_usd_rub_price = current_prices_of_assets.get('USDTRUB', None)

            for asset in user_assets:
                self._add_active_in_persons_portfolio(ident=asset.token,
                                                      lot=asset.lot,
                                                      average_price_buy_in_rub=asset.average_price_in_rub,
                                                      average_price_buy_in_usd=asset.average_price_in_usd,
                                                      current_price=self._get_current_price(current_prices_of_assets,
                                                                                            asset),
                                                      currency='usd',
                                                      name=asset.token,
                                                      pk=asset.pk)
        except (AttributeError, KeyError) as ex:
            logger.warning(ex)

    @staticmethod
    def _get_tokens_for_binance_api(personal_assets):
        """
         Формирует список токенов для запроса текущих цен криптовалют на бирже Binance.
        :param personal_assets:
        :return:
        """
        try:
            return [f"usdt{asset.token}" if asset.token == 'rub' else f'{asset.token}usdt'
                    for asset in personal_assets]
        except (AttributeError, TypeError) as ex:
            logger.warning(ex)

    @staticmethod
    def _get_current_price(current_prices, asset):
        """
        Возвращает текущую цену криптовалютного актива.
        :param current_prices:
        :param asset:
        :return:
        """
        try:
            if asset.token in ('usd', 'rub', 'usdc', 'usdt', 'busd'):
                return 1
            return current_prices.get(asset.token.upper() + 'USDT', None)
        except (KeyError, AttributeError, TypeError) as ex:
            logger.warning(ex)


class StockPortfolio(Portfolio):
    def __init__(self, user: User, assets: List[UserStock]):
        super().__init__(type_of_assets='stock', user=user)
        self._make_portfolio(assets)

    def _make_portfolio(self, user_assets):
        try:
            figis = [asset.figi for asset in user_assets]
            currencies, names = self._get_currencies_and_names_from_bd(figis)
            current_prices_of_assets = TinkoffAPI.get_last_price_asset(figi=figis)
            self._current_usd_rub_price = current_prices_of_assets.get(self.USD_RUB_FIGI, 0)

            for asset in user_assets:
                self._add_active_in_persons_portfolio(
                    ident=asset.figi,
                    lot=asset.lot,
                    average_price_buy_in_rub=asset.average_price_in_rub,
                    average_price_buy_in_usd=asset.average_price_in_usd,
                    current_price=current_prices_of_assets.get(asset.figi, None),
                    currency=currencies.get(asset.figi, None),
                    name=names.get(asset.figi, None),
                    pk=asset.pk
                )

        except (AttributeError, KeyError) as ex:
            logger.warning(ex)


class PortfolioMaker:
    def __init__(self, assets_type: str, user: User, assets: Union[List[UserStock], List[PersonsCrypto]] = None):
        portfolio_class = self._get_assets_class(assets_type)

        if not assets:
            assets = self._get_user_assets(user=user, assets_type=assets_type)

        self.portfolio = portfolio_class(user=user, assets=assets)

    @staticmethod
    def _get_assets_class(assets_type):
        assets_classes = {
            'crypto': CryptoPortfolio,
            'stock': StockPortfolio
        }
        if assets_type not in assets_classes:
            raise ValueError(f"Unsupported assets_type: {assets_type}")
        return assets_classes[assets_type]

    @staticmethod
    def _get_user_assets(assets_type, user):
        return PortfolioConfig.users_models[assets_type].objects.filter(user=user)

# //TODO сделать чтообы актив не отображался если маленький баланс
