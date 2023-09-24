from collections import Counter
from typing import Union
import logging

from django.db.models import Sum

from crypto.binanceAPI import BinanceAPI
from crypto.models import PersonsCrypto, PersonsTransactions, CryptoInvest
from stocks.models import UserStock, Share, Bond, Etf, Currency, UserTransaction, StockInvest
from stocks.services.tinkoff_API import TinkoffAPI

logger = logging.getLogger('main')
logger_debug = logging.getLogger('debug')


class PersonPortfolioConfig:
    # параметр, который идет в метод 'round'
    ROUND_DIGIT = 1
    ROUND_DIGIT_LOT = 4

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
        'stock': StockInvest
    }
    _models_for_shares_bonds_etfs_currencies = {
        'shares': Share,
        'bonds': Bond,
        'etfs': Etf,
        'currencies': Currency
    }


class ArithmeticOperations:

    @staticmethod
    def count_percent_profit(start_price: Union[int, float], now_price: Union[int, float]) -> float:
        """
        Считает процентное изменение стоимости с start_price до now_price актива.

        Args:
            start_price (Union[int, float]): Начальная стоимость актива.
            now_price (Union[int, float]): Текущая стоимость актива.

        Returns:
            float: Процентное изменение стоимости.
        """
        if not start_price or not now_price:
            return 0

        try:
            return (now_price / start_price - 1) * 100
        except TypeError as ex:
            logger.warning(ex)
            return 0

    @staticmethod
    def get_new_average_price(old_average_price: Union[int, float],
                              new_price: Union[int, float],
                              old_size: Union[int, float],
                              new_buy_size: Union[int, float]) -> float:
        """
        Рассчитывает новую среднюю стоимость актива.

        Args:
            old_average_price (Union[int, float]): Старая средняя стоимость актива.
            new_price (Union[int, float]): Цена новой покупки актива.
            old_size (Union[int, float]): Старый размер актива.
            new_buy_size (Union[int, float]): Размер новой покупки актива.

        Returns:
            float: Новая средняя стоимость актива.
            """
        try:
            return (old_size * old_average_price + new_buy_size * new_price) / (new_buy_size + old_size)
        except (ZeroDivisionError, TypeError) as ex:
            logger.warning(ex)
            return 0

    @classmethod
    def round_number(cls, number: float, round_digit: int = PersonPortfolioConfig.ROUND_DIGIT) -> float:
        """
        Округляет число number до указанных разрядов.

        Args:
            number (float): Число, которое нужно округлить.
            round_digit (int, optional): Количество разрядов для округления.
                Если не указано, будет использовано значение
                из PersonPortfolioConfig.ROUND_DIGIT.

        Returns:
            float: Округленное число.
        """
        return round(number, round_digit)


class AssetsInfo(ArithmeticOperations, PersonPortfolioConfig):
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
            self.profit_in_percent_rub = self.count_percent_profit(self.average_price_buy_in_rub * self.lot,
                                                              self.total_now_balance_in_rub)
            self.profit_in_percent_usd = self.count_percent_profit(self.average_price_buy_in_usd * self.lot,
                                                              self.total_now_balance_in_usd)
        except KeyError as ex:
            logger.warning(ex)

    def __count_profits_in_currencies(self) -> None:
        """Вычисляет прибыль актива в валюте (в рублях и долларах)"""
        try:
            self.profit_in_currency_rub = self.total_now_balance_in_rub - self.average_price_buy_in_rub * self.lot
            self.profit_in_currency_usd = self.total_now_balance_in_usd - self.average_price_buy_in_usd * self.lot
            logger_debug.debug(self.profit_in_currency_usd)
        except TypeError as ex:
            logger.warning(ex)

    def __get_assets_balance_in_currencies(self, **kwargs) -> tuple[float, float]:
        """Возвращает текущую стоимость бумаги в портфеле на основе ее количества и текущей цены в формате
        (стоимость в рублях, стоимость в долларах)"""
        try:
            if PortfolioBalance.check_currency_is_usd(self.currency):
                total_now_balance_in_rub = self.current_price * self.lot * self.usd_rub_currency
                total_now_balance_in_usd = self.current_price * self.lot
            else:
                total_now_balance_in_rub = self.current_price * self.lot
                total_now_balance_in_usd = self.current_price * self.lot / self.usd_rub_currency
            return total_now_balance_in_rub, total_now_balance_in_usd
        except (TypeError, KeyError) as ex:
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
                           aggregate(invest_sum_in_rub=Sum('invest_sum_in_rub'),
                                     invest_sum_in_usd=Sum('invest_sum_in_usd')))

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

        try:
            for ticker, info in self._tickers.items():
                tickers_info[ticker] = {
                    'name': info.name,
                    'lot': ArithmeticOperations.round_number(info.lot, self.ROUND_DIGIT_LOT),
                    'average_price_buy_in_rub': ArithmeticOperations.round_number(info.average_price_buy_in_rub),
                    'average_price_buy_in_usd': ArithmeticOperations.round_number(info.average_price_buy_in_usd),
                    'current_price': info.current_price,
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
                        ArithmeticOperations.round_number(info._count_percent_of_portfolio(self._total_balance_in_usd)),
                    'pk': info.pk,
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
    def __init__(self, user, assets):
        super().__init__(type_of_assets='crypto', user=user)
        self.__make_portfolio(assets)

    def __make_portfolio(self, user_assets):
        try:
            tokens = self._get_tokens_for_binance_api(user_assets)
            current_prices_of_assets = BinanceAPI.get_tickers_prices(tokens)
            # //TODO вынести инвест суммы в один класс
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
        except (AttributeError, TypeError) as ex:
            logger.warning(ex)

    @staticmethod
    def _get_current_price(current_prices, asset):
        try:
            if asset.token in ('usd', 'rub', 'usdc', 'usdt', 'busd'):
                return 1
            return current_prices.get(asset.token.upper() + 'USDT', None)
        except (KeyError, AttributeError, TypeError) as ex:
            logger.warning(ex)


class StockPortfolio(PersonsPortfolio):
    def __init__(self, user, user_assets):
        super().__init__(type_of_assets='stock', user=user)
        self.__make_portfolio(user_assets)

    def __make_portfolio(self, user_assets):
        try:
            figis = [asset.figi for asset in user_assets]
            currencies, names = self._get_currencies_and_names_from_bd(figis)
            current_prices_of_assets = TinkoffAPI.get_last_price_asset(figi=figis)

            self._handle_portfolio_assets(user_assets, currencies, names, current_prices_of_assets)

        except (AttributeError, KeyError) as ex:
            logger.warning(ex)

    def _handle_portfolio_assets(self, user_assets, currencies, names, current_prices_of_assets):
        try:
            self._current_usd_rub_price = current_prices_of_assets.get(self.USD_RUB_FIGI, None)

            for asset in user_assets:
                figi = asset.figi
                lot = asset.lot
                average_price_buy_in_rub = asset.average_price_in_rub
                average_price_buy_in_usd = asset.average_price_in_usd
                current_price = current_prices_of_assets.get(figi, None)
                currency = currencies.get(figi, None)
                name = names.get(figi, None)
                pk = asset.pk

                self._add_active_in_persons_portfolio(
                    ident=figi,
                    lot=lot,
                    average_price_buy_in_rub=average_price_buy_in_rub,
                    average_price_buy_in_usd=average_price_buy_in_usd,
                    current_price=current_price,
                    currency=currency,
                    name=name,
                    pk=pk
                )
        except (AttributeError, KeyError) as ex:
            logger.warning(ex)


# //TODO сделать чтообы актив не отображался если маленький баланс
