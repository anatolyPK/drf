from typing import Union
import logging

from django.db.models import Sum

from crypto.binanceAPI import BinanceAPI
from crypto.models import PersonsCrypto, PersonsTransactions, CryptoInvest
from stocks.models import UserStock, Share, Bond, Etf, Currency, UserTransaction
from stocks.services.tinkoff_API import TinkoffAPI


logger = logging.getLogger('main')
# //TODO middleware скорость views


class PersonPortfolioConfig:
    # параметр, который идет в метод 'round'
    ROUND_DIGIT = 2

    USD_RUB_FIGI = 'BBG0013HGFT4'

    _users_models = {
        'crypto': PersonsCrypto,
        'stock': UserStock
    }

    _users_transactions_models = {
        'crypto': PersonsTransactions,
        'stock': UserTransaction
    }

    _users_invest_sum_models = {
        'crypto': CryptoInvest,
        'stock': ...
    }
    _models_for_shares_bonds_etfs_currencies = {
        'shares': Share,
        'bonds': Bond,
        'etfs': Etf,
        'currencies': Currency
    }


class ArithmeticOperations:

    @staticmethod
    def count_percent_profit(start_price: Union[int, float],
                             now_price: Union[int, float]) -> float:
        """Считает изменение стоимости с start_price до now_price актива в процентах"""
        try:
            return (now_price / start_price - 1) * 100
        except ZeroDivisionError as ex:
            logger.warning(ex)
            return 0
        except TypeError as ex:
            logger.warning(ex)
            return 0

    @staticmethod
    def get_new_average_price(old_average_price: Union[int, float],
                              new_price: Union[int, float],
                              old_size: Union[int, float],
                              new_buy_size: Union[int, float]) -> float:
        """Рассчитывает новую среднюю стоимость актива"""
        try:
            return (old_size * old_average_price + new_buy_size * new_price) / (new_buy_size + old_size)
        except ZeroDivisionError as ex:
            logger.warning(ex)
            return 0
        except TypeError as ex:
            logger.warning(ex)
            return 0

    @staticmethod
    def add_plus_if_more_than_zero(profit_in_currency_rub: Union[int, float]) -> str:
        """Превращает число в строку, добавяляя +, если оно больше нуля:
        52 -> '+52
        99 -> '+99''"""
        try:
            return str(profit_in_currency_rub) if profit_in_currency_rub <= 0 else '+' + str(profit_in_currency_rub)
        except TypeError as ex:
            logger.warning(ex)


class AssetsInfo(ArithmeticOperations, PersonPortfolioConfig):
    """Класс, хранящий информацию о конкретном активе"""

    def __init__(self, **kwargs):
        try:
            self.ident = kwargs['ident']
            self.name = kwargs['name']
            self.lot = kwargs['lot']
            self.average_price_buy_in_rub = kwargs['average_price_buy_in_rub']
            self.average_price_buy_in_usd = kwargs['average_price_buy_in_usd']
            self.current_price = kwargs['current_price']
            self.usd_rub_currency = kwargs['usd_rub_currency']
            self.currency = kwargs['currency']
            self.total_now_balance_in_rub, self.total_now_balance_in_usd = \
                self.__get_assets_balance_in_currencies(**kwargs)
            self.__count_profits_in_currencies()
            self.__count_profits_in_percents()
        except KeyError as ex:
            logger.warning(ex)

    def _count_percent_of_portfolio(self, portfolio_balance: float) -> float:
        """Вычисляет процент актива от всего портфеля"""
        return self.total_now_balance_in_usd / portfolio_balance * 100

    def __count_profits_in_percents(self) -> None:
        """Вычисляет прибыль актива в процентах (в рублях и долларах)"""
        try:
            profit_in_percent_rub = self.count_percent_profit(self.average_price_buy_in_rub * self.lot,
                                                              self.total_now_balance_in_rub)
            rounded_profit_in_percent_rub = round(profit_in_percent_rub, self.ROUND_DIGIT)
            self.profit_in_percent_rub = self.add_plus_if_more_than_zero(rounded_profit_in_percent_rub)

            profit_in_percent_usd = self.count_percent_profit(self.average_price_buy_in_usd * self.lot,
                                                              self.total_now_balance_in_usd)
            rounded_profit_in_percent_usd = round(profit_in_percent_usd, self.ROUND_DIGIT)
            self.profit_in_percent_usd = self.add_plus_if_more_than_zero(rounded_profit_in_percent_usd)
        except KeyError as ex:
            logger.warning(ex)

    def __count_profits_in_currencies(self) -> None:
        """Вычисляет прибыль актива в валюте (в рублях и долларах)"""
        try:
            profit_in_currency_rub = round(self.total_now_balance_in_rub - self.average_price_buy_in_rub * self.lot,
                                           self.ROUND_DIGIT)
            profit_in_currency_usd = round(self.total_now_balance_in_usd - self.average_price_buy_in_usd * self.lot,
                                           self.ROUND_DIGIT)
            self.profit_in_currency_rub = self.add_plus_if_more_than_zero(profit_in_currency_rub)
            self.profit_in_currency_usd = self.add_plus_if_more_than_zero(profit_in_currency_usd)
        except TypeError as ex:
            logger.warning(ex)

    def __get_assets_balance_in_currencies(self, **kwargs) -> tuple[float, float]:
        """Возвращает текущую стоимость бумаги в портфеле на основе ее количества и текущей цены в формате
        (стоимость в рублях, стоимость в долларах)"""
        try:
            if PortfolioBalance.check_currency_is_usd(kwargs['currency']):
                return kwargs['current_price'] * kwargs['lot'] * self.usd_rub_currency, \
                       kwargs['current_price'] * kwargs['lot']
            else:
                return kwargs['current_price'] * kwargs['lot'], \
                       kwargs['current_price'] * kwargs['lot'] / self.usd_rub_currency
        except TypeError as ex:
            logger.warning(ex)
        except KeyError as ex:
            logger.warning(ex)


class PortfolioBalance(PersonPortfolioConfig):
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
        try:
            if self.check_currency_is_usd(kwargs['currency']):
                self._total_balance_in_rub += kwargs['current_price'] * kwargs['lot'] * self._current_usd_rub_price
                self._total_balance_in_usd += kwargs['current_price'] * kwargs['lot']
            else:
                self._total_balance_in_rub += kwargs['current_price'] * kwargs['lot']
                self._total_balance_in_usd += kwargs['current_price'] * kwargs['lot'] / self._current_usd_rub_price
        except KeyError as ex:
            logger.warning(ex)
        except ZeroDivisionError as ex:
            logger.warning(ex)
        except TypeError as ex:
            logger.warning(ex)

    def _add_price_in_buy_price(self, **kwargs):
        try:
            self._buy_price_in_rub += kwargs['average_price_buy_in_rub'] * kwargs['lot']
            self._buy_price_in_usd += kwargs['average_price_buy_in_usd'] * kwargs['lot']
        except KeyError as ex:
            logger.warning(ex)
        except TypeError as ex:
            logger.warning(ex)

    @staticmethod
    def check_currency_is_usd(currency):
        """Проверяет тип валюты. Если $, то возвращает True, иначе False"""
        if currency in ('usd', 'usdt'):
            return True
        return False

    def _set_usdt_rub_currency(self, current_price: float):
        self._current_usd_rub_price = current_price


class PersonsPortfolioDB(PortfolioBalance):
    def _get_datas_from_model(self):
        try:
            return self._users_models[self._type_of_assets].objects.all().filter(user=self._user)
        except KeyError as ex:
            logger.warning(ex)
        except ValueError as ex:
            logger.warning(ex)

    def _get_currencies_and_names_from_bd(self, figis):
        currencies, names = {}, {}
        try:
            for db_name in self._models_for_shares_bonds_etfs_currencies.values():
                assets_from_bd = db_name.objects.all().filter(figi__in=figis)
                for asset in assets_from_bd:
                    currencies[asset.figi] = asset.currency
                    names[asset.figi] = asset.name
        except ValueError as ex:
            logger.warning(ex)
        return currencies, names

    def get_invest_sum(self) -> tuple[float, float]:
        """Возвращает сумму инвестирования в формате (сумма в рублях, сумма в долларах).
        Если нет записей - возвращает: (0, 0), (0, 1)"""

        invest_sum_dict = (self._users_invest_sum_models[self._type_of_assets].objects.filter(user=self._user).
                aggregate(invest_sum_in_rub=Sum('invest_sum_in_rub'), invest_sum_in_usd=Sum('invest_sum_in_usd')))

        return (0 if invest_sum_dict['invest_sum_in_rub'] is None else invest_sum_dict['invest_sum_in_rub'],
                0 if invest_sum_dict['invest_sum_in_usd'] is None else invest_sum_dict['invest_sum_in_usd'])


class PersonsPortfolio(PersonsPortfolioDB, ArithmeticOperations):
    """Класс для работы с портфелем пользователя."""

    def __init__(self, *, type_of_assets: str, user):
        super().__init__(type_of_assets=type_of_assets,
                         user=user)
        self._tickers = {}
        self.invest_sum_in_rub, self.invest_sum_in_usd = self.get_invest_sum()

    def _add_active_in_persons_portfolio(self, **kwargs):
        """Добавление актива в портфель"""
        self._add_price_in_total_and_buy_balance(**kwargs)
        try:
            self._tickers[kwargs['ident']] = AssetsInfo(usd_rub_currency=self._current_usd_rub_price, **kwargs)
        except KeyError as ex:
            logger.warning(ex)

    def get_info_about_portfolio_and_assets(self) -> dict:
        """Возвращает информацию о портфеле, а также об активах."""
        portfolios_info = self.get_info_about_portfolio()

        try:
            portfolios_info['assets'] = self.get_info_about_assets()
        except TypeError as ex:
            logger.warning(ex)

        return portfolios_info

    def get_info_about_portfolio(self) -> dict:
        """Возвращает информацию о портфеле"""
        params_dict = {'total_balance_in_rub': round(self._total_balance_in_rub, self.ROUND_DIGIT),
                       'total_balance_in_usd': round(self._total_balance_in_usd, self.ROUND_DIGIT),
                       'buy_price_in_rub': round(self._buy_price_in_rub, self.ROUND_DIGIT),
                       'buy_price_in_usd': round(self._buy_price_in_usd, self.ROUND_DIGIT),
                       'profit_in_percents_rub': self.add_plus_if_more_than_zero(
                           round(self.count_percent_profit(self._buy_price_in_rub, self._total_balance_in_rub),
                                 self.ROUND_DIGIT)),
                       'profit_in_percents_usd': self.add_plus_if_more_than_zero(
                           round(self.count_percent_profit(self._buy_price_in_usd, self._total_balance_in_usd),
                                 self.ROUND_DIGIT)),
                       'profit_in_currency_rub': self.add_plus_if_more_than_zero(
                           round(self._total_balance_in_rub - self._buy_price_in_rub, self.ROUND_DIGIT)),
                       'profit_in_currency_usd': self.add_plus_if_more_than_zero(
                           round(self._total_balance_in_usd - self._buy_price_in_usd, self.ROUND_DIGIT)),
                       'usd_rub_currency': round(self._current_usd_rub_price, self.ROUND_DIGIT),
                       'profit_invest_in_rub_in_percent':  self.add_plus_if_more_than_zero(
                           round(self.count_percent_profit(self.invest_sum_in_rub, self._total_balance_in_rub),
                                 self.ROUND_DIGIT)),
                       'profit_invest_in_usd_in_percent': self.add_plus_if_more_than_zero(
                           round(self.count_percent_profit(self.invest_sum_in_usd, self._total_balance_in_usd),
                                 self.ROUND_DIGIT)),
                       'profit_invest_in_rub_in_currency': self.add_plus_if_more_than_zero(
                           round(self._total_balance_in_rub - self.invest_sum_in_rub, self.ROUND_DIGIT)),
                       'profit_invest_in_usd_in_currency': self.add_plus_if_more_than_zero(
                           round(self._total_balance_in_usd - self.invest_sum_in_usd, self.ROUND_DIGIT)),
                       }
        return params_dict

    def get_info_about_assets(self) -> dict:
        """Возвращает информацию об активах. Возвращает словарь активов, отсортированных по доле в портфеле
        (от самого большого)"""
        tickers_info = {}

        try:
            for ticker in self._tickers:
                tickers_info[ticker] = {
                    'name': self._tickers[ticker].name,
                    'lot': self._tickers[ticker].lot,
                    'average_price_buy_in_rub': round(self._tickers[ticker].average_price_buy_in_rub, self.ROUND_DIGIT),
                    'average_price_buy_in_usd': round(self._tickers[ticker].average_price_buy_in_usd, self.ROUND_DIGIT),
                    'current_price': self._tickers[ticker].current_price,
                    'currency': self._get_currency_symbol(self._tickers[ticker].currency),
                    'profit_in_currency_rub': self._tickers[ticker].profit_in_currency_rub,
                    'profit_in_currency_usd': self._tickers[ticker].profit_in_currency_usd,
                    'profit_in_percent_rub': self._tickers[ticker].profit_in_percent_rub,
                    'profit_in_percent_usd': self._tickers[ticker].profit_in_percent_usd,
                    'total_now_balance_in_rub': round(self._tickers[ticker].total_now_balance_in_rub, self.ROUND_DIGIT),
                    'total_now_balance_in_usd': round(self._tickers[ticker].total_now_balance_in_usd, self.ROUND_DIGIT),
                    'profit_in_currency': self._tickers[ticker].profit_in_currency_usd,
                    'profit_in_percent': self._tickers[ticker].profit_in_percent_usd,
                    'total_now_balance': round(self._tickers[ticker].total_now_balance_in_usd, self.ROUND_DIGIT),
                    'percent_of_portfolio': round(self._tickers[ticker]._count_percent_of_portfolio(self._total_balance_in_usd),
                                                  self.ROUND_DIGIT)
                }

        except KeyError as ex:
            logger.warning(ex)

        return dict(sorted(tickers_info.items(), key=lambda item: item[1]['percent_of_portfolio'], reverse=True))

    def _get_currency_symbol(self, currency):
        if currency.lower() in ('usd', 'usdt'):
            return '$'
        elif currency.lower() == 'rub':
            return '₽'


class CryptoPortfolio(PersonsPortfolio):
    def __init__(self, user):
        super().__init__(type_of_assets='crypto', user=user)
        self.__make_portfolio()

    def __make_portfolio(self):
        personal_assets = self._get_datas_from_model()
        tokens = self._get_tokens_for_binance_api(personal_assets)
        current_prices_of_assets = BinanceAPI.get_tickers_prices(tokens)
        # //TODO вынести инвест суммы в один класс

        try:
            self._set_usdt_rub_currency(current_prices_of_assets['USDTRUB'])
        except KeyError as ex:
            logger.warning(ex)

        try:
            for asset in personal_assets:
                self._add_active_in_persons_portfolio(ident=asset.token,
                                                      lot=asset.lot,
                                                      average_price_buy_in_rub=asset.average_price_in_rub,
                                                      average_price_buy_in_usd=asset.average_price_in_usd,
                                                      current_price=self._get_current_price(current_prices_of_assets,
                                                                                            asset),
                                                      currency='usd',
                                                      name=asset.token)
        except AttributeError as ex:
            logger.warning(ex)

    def __check_is_usd_rub(self, asset):
        if asset.token in ('usd', 'usdt', 'usdc', 'busd'):
            return True
        return False

    @staticmethod
    def _get_tokens_for_binance_api(personal_assets):
        tokens = []
        try:
            for asset in personal_assets:
                if asset.token == 'rub':
                    tokens.append('usdt' + asset.token)
                else:
                    tokens.append(asset.token + 'usdt')
            return tokens
        except AttributeError as ex:
            logger.warning(ex)
        except TypeError as ex:
            logger.warning(ex)

    @staticmethod
    def _get_current_price(current_prices, asset):
        try:
            if asset.token in ('usd', 'rub', 'usdc', 'usdt', 'busd'):
                return 1
            return current_prices[asset.token.upper() + 'USDT']

        except KeyError as ex:
            logger.warning(ex)
        except AttributeError as ex:
            logger.warning(ex)
        except TypeError as ex:
            logger.warning(ex)


class StockPortfolio(PersonsPortfolio):
    def __init__(self, user):
        super().__init__(type_of_assets='stock', user=user)
        self.__make_portfolio()

    def __make_portfolio(self):
        try:
            personal_assets = self._get_datas_from_model()
            figis = [asset.figi for asset in personal_assets]
            # //TODO join доставвать cur и names
            currencies, names = self._get_currencies_and_names_from_bd(figis)
            current_prices_of_assets = TinkoffAPI.get_last_price_asset(figi=figis)
            self._set_usdt_rub_currency(current_prices_of_assets[self.USD_RUB_FIGI])
            for asset in personal_assets:
                self._add_active_in_persons_portfolio(ident=asset.figi,
                                                      lot=asset.lot,
                                                      average_price_buy_in_rub=asset.average_price_in_rub,
                                                      average_price_buy_in_usd=asset.average_price_in_usd,
                                                      current_price=current_prices_of_assets[asset.figi],
                                                      currency=currencies[asset.figi],
                                                      name=names[asset.figi])
        except AttributeError as ex:
            logger.warning(ex)
        except KeyError as ex:
            logger.warning(ex)
