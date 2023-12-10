from portfolio.services.arithmetics import ArithmeticOperations

import logging

from portfolio.services.config import PortfolioConfig
from stocks.models import Bond
from stocks.services.bonds_calculator import BondCalculator

logger = logging.getLogger('main')
logger_debug = logging.getLogger('debug')


class AssetInfo:
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
            self._lot = kwargs['lot']
            self._average_price_buy_in_rub = kwargs['average_price_buy_in_rub']
            self._average_price_buy_in_usd = kwargs['average_price_buy_in_usd']
            self._current_price = kwargs['current_price']
            self._usd_rub_currency = kwargs['usd_rub_currency']
            self.currency = kwargs['currency']
            self.pk = kwargs['pk']

            # if kwargs.get('stock_tag', None):  # только для фонды. можно также сделать привязку к портфелям
            self._stock_tag = kwargs.get('stock_tag', None)

            self._total_now_balance_in_rub, self._total_now_balance_in_usd = \
                ArithmeticOperations.count_rub_and_usd_price(currency=self.currency,
                                                             current_price=self._current_price,
                                                             lot=self._lot,
                                                             usd_rub_currency=self._usd_rub_currency)
            self._profit_in_currency_rub, self._profit_in_currency_usd = self._count_profits_in_currencies()
            self._profit_in_percent_rub, self._profit_in_percent_usd = self._count_profits_in_percents()

            self._profit_in_currency = self._get_profit_in_currency()
            self._profit_in_percent = self._get_profit_in_percent()
            self._total_balance = self._get_total_balance()
            self._average_price_buy = self._get_average_buy_price()

            self._percent_of_portfolio = 0
            self._portfolio_balance_usd = None

            if isinstance(kwargs['asset_typ'], Bond):
                bond_calculator = BondCalculator(kwargs['asset_typ'], '0')
                self.rounded_ytm = bond_calculator.rounded_ytm
                self.rounded_adjusted_current_yield = bond_calculator.rounded_adjusted_current_yield
        except KeyError as ex:
            logger.warning((kwargs, ex))

    def _count_profits_in_percents(self) -> tuple[float, float]:
        """Вычисляет прибыль актива в процентах (в рублях и долларах)"""
        profit_in_percent_rub = ArithmeticOperations.count_percent_profit(self._average_price_buy_in_rub * self._lot,
                                                                          self._total_now_balance_in_rub)
        profit_in_percent_usd = ArithmeticOperations.count_percent_profit(self._average_price_buy_in_usd * self._lot,
                                                                          self._total_now_balance_in_usd)
        return profit_in_percent_rub, profit_in_percent_usd

    def _count_profits_in_currencies(self) -> tuple[float, float]:
        """Вычисляет прибыль актива в валюте (в рублях и долларах)"""
        try:
            profit_in_currency_rub = self._total_now_balance_in_rub - self._average_price_buy_in_rub * self._lot
            profit_in_currency_usd = self._total_now_balance_in_usd - self._average_price_buy_in_usd * self._lot
        except TypeError as ex:
            logger.warning(ex)
        else:
            return profit_in_currency_rub, profit_in_currency_usd

    def _get_profit_in_currency(self):
        if self._check_currency_is_rub():
            return self._profit_in_currency_rub
        return self._profit_in_currency_usd

    def _get_average_buy_price(self):
        if self._check_currency_is_rub():
            return self._average_price_buy_in_rub
        return self._average_price_buy_in_usd

    def _get_profit_in_percent(self):
        if self._check_currency_is_rub():
            return self._profit_in_percent_rub
        return self._profit_in_percent_usd

    def _get_total_balance(self):
        if self._check_currency_is_rub():
            return self._total_now_balance_in_rub
        return self._total_now_balance_in_usd

    def _check_currency_is_rub(self):
        return self.currency == 'rub'


class Asset(AssetInfo):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def current_price(self):
        return ArithmeticOperations.round_balance(self._current_price, is_price=True)

    @property
    def profit_in_currency(self):
        return ArithmeticOperations.round_balance(self._profit_in_currency)

    @property
    def profit_in_percent(self):
        return ArithmeticOperations.round_balance(self._profit_in_percent)

    @property
    def total_balance(self):
        return ArithmeticOperations.round_balance(self._total_balance)

    @property
    def average_price_buy(self):
        return ArithmeticOperations.round_balance(self._average_price_buy)

    @property
    def lot(self):
        return ArithmeticOperations.round_balance(self._lot, is_lot=True)

    @property #refactor eti tagi
    def stock_tag(self):
        return self._stock_tag if self._stock_tag else None

    @property
    def percent_of_portfolio(self):
        return ArithmeticOperations.round_balance(self._percent_of_portfolio)

    @property
    def portfolio_balance_usd(self):
        return self._portfolio_balance_usd

    @portfolio_balance_usd.setter
    def portfolio_balance_usd(self, total_balance_in_usd):
        self._percent_of_portfolio = ArithmeticOperations.count_percent(self._total_now_balance_in_usd,
                                                                        total_balance_in_usd)
