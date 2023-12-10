from django.utils import timezone

from portfolio.services.arithmetics import ArithmeticOperations
from portfolio.services.assets import Asset
from ..config import PortfolioConfig
from typing import Tuple
from django.db.models import Sum

import logging

logger = logging.getLogger('main')
logger_debug = logging.getLogger('debug')


class PersonsPortfolioDB(PortfolioConfig):
    @classmethod
    def _get_users_assets_from_model(cls, user, type_of_assets, assets=None):
        """
        Возвращает активы пользователя на основе модели соответствующего типа.
        assets: [share, bond, etf, currency]
        """
        try:
            if assets is not None:
                return cls.users_models[type_of_assets][assets].objects.filter(user=user)

            return cls.users_models[type_of_assets].objects.filter(user=user)

        except (KeyError, ValueError) as ex:
            logger.warning(ex)
            return None

    @classmethod
    def get_invest_sum(cls, type_of_assets, user) -> Tuple[float, float]:
        """
        Возвращает сумму инвестирования в формате (сумма в рублях, сумма в долларах).
        Если нет записей - возвращает: (0, 0), (0, 1)
        """
        invest_sum_dict = (cls._users_invest_sum_models[type_of_assets].objects.filter(user=user).
                           aggregate(invest_sum_in_rub=Sum('invest_sum_in_rub'),
                                     invest_sum_in_usd=Sum('invest_sum_in_usd')))

        invest_sum_rub = invest_sum_dict.get('invest_sum_in_rub', 0) or 0
        invest_sum_usd = invest_sum_dict.get('invest_sum_in_usd', 0) or 0

        return invest_sum_rub, invest_sum_usd

    @classmethod
    def get_invest_operation(cls, type_of_assets, user):
        return cls._users_invest_sum_models[type_of_assets].objects.filter(user=user)


class BasePortfolio(PortfolioConfig):
    def __init__(self, type_of_assets, user):
        self.user = user
        self.type_of_assets = type_of_assets
        self.assets = {}
        self.current_usd_rub_price = 0

        self._buy_price_in_rub = 0
        self._buy_price_in_usd = 0
        self._total_balance_in_rub = 0
        self._total_balance_in_usd = 0
        self._profit_in_percent_rub = 0
        self._profit_in_percent_usd = 0
        self._profit_in_currency_rub = 0
        self._profit_in_currency_usd = 0

        self._invest_sum_in_rub = 0
        self._invest_sum_in_usd = 0
        self._profit_invest_in_percent_rub = 0
        self._profit_invest_in_percent_usd = 0
        self._profit_invest_in_currency_rub = 0
        self._profit_invest_in_currency_usd = 0
        self._irr_rub = 0
        self._irr_usd = 0


class PortfolioBalanceCounter(BasePortfolio):
    def __init__(self, *, type_of_assets: str, user):
        super().__init__(type_of_assets=type_of_assets, user=user)
        self._set_invest_sum()
        self.count_profits_flag = False

    def count_profits(self):
        self._count_profit_in_currency()
        self._count_profit_in_percent()
        self._count_invest_profit_in_currency()
        self._count_invest_profit_in_percent()
        self.count_irr()

    def _count_profit_in_currency(self):
        self._profit_in_currency_rub = self._total_balance_in_rub - self._buy_price_in_rub
        self._profit_in_currency_usd = self._total_balance_in_usd - self._buy_price_in_usd

    def _count_profit_in_percent(self):
        self._profit_in_percent_rub = ArithmeticOperations.count_percent_profit(self._buy_price_in_rub,
                                                                                self._total_balance_in_rub)
        self._profit_in_percent_usd = ArithmeticOperations.count_percent_profit(self._buy_price_in_usd,
                                                                                self._total_balance_in_usd)

    def _count_invest_profit_in_currency(self):
        self._profit_invest_in_currency_rub = self._total_balance_in_rub - self._invest_sum_in_rub
        self._profit_invest_in_currency_usd = self._total_balance_in_usd - self._invest_sum_in_usd

    def _count_invest_profit_in_percent(self):
        self._profit_invest_in_percent_rub = ArithmeticOperations.count_percent_profit(self._invest_sum_in_rub,
                                                                                       self._total_balance_in_rub)
        self._profit_invest_in_percent_usd = ArithmeticOperations.count_percent_profit(self._invest_sum_in_usd,
                                                                                       self._total_balance_in_usd)

    def count_irr(self):
        invest_operations = PersonsPortfolioDB.get_invest_operation(type_of_assets=self.type_of_assets, user=self.user)
        if invest_operations:
            dates = [operation.date_operation for operation in invest_operations] + [timezone.now().date()]
            summ_rub = [operation.invest_sum_in_rub for operation in invest_operations] + [-self._total_balance_in_rub]
            summ_usd = [operation.invest_sum_in_usd for operation in invest_operations] + [-self._total_balance_in_usd]

            self._irr_rub = ArithmeticOperations.calculate_irr(dates, summ_rub) * 100
            self._irr_usd = ArithmeticOperations.calculate_irr(dates, summ_usd) * 100

    # сдела
    def _set_invest_sum(self):
        self._invest_sum_in_rub, self._invest_sum_in_usd = \
            PersonsPortfolioDB.get_invest_sum(user=self.user, type_of_assets=self.type_of_assets)

    def add_price_in_total_and_buy_balance(self, **kwargs) -> None:
        self._add_price_in_total_balance(**kwargs)
        self._add_price_in_buy_price(**kwargs)

    def _add_price_in_total_balance(self, **kwargs):
        price_in_rub, price_in_usd = ArithmeticOperations.count_rub_and_usd_price(currency=kwargs['currency'],
                                                                                  current_price=kwargs['current_price'],
                                                                                  lot=kwargs['lot'],
                                                                                  usd_rub_currency=self.current_usd_rub_price)
        self._total_balance_in_rub += price_in_rub
        self._total_balance_in_usd += price_in_usd

    def _add_price_in_buy_price(self, **kwargs):
        try:
            self._buy_price_in_rub += kwargs['average_price_buy_in_rub'] * kwargs['lot']
            self._buy_price_in_usd += kwargs['average_price_buy_in_usd'] * kwargs['lot']
        except (KeyError, TypeError) as ex:
            logger.warning((kwargs, ex))


class Portfolio(PortfolioBalanceCounter):
    """Класс для работы с портфелем пользователя."""

    def __init__(self, *, type_of_assets: str, user):
        super().__init__(type_of_assets=type_of_assets, user=user)

    @property
    def total_balance_in_rub(self):
        return ArithmeticOperations.round_balance(self._total_balance_in_rub)

    @property
    def total_balance_in_usd(self):
        return ArithmeticOperations.round_balance(self._total_balance_in_usd)

    @property
    def invest_sum_in_rub(self):
        return ArithmeticOperations.round_balance(self._invest_sum_in_rub)

    @property
    def invest_sum_in_usd(self):
        return ArithmeticOperations.round_balance(self._invest_sum_in_usd)

    @property
    def profit_in_currency_rub(self):
        self._check_profits_count()
        return ArithmeticOperations.round_balance(self._profit_in_currency_rub)

    @property
    def profit_in_currency_usd(self):
        self._check_profits_count()
        return ArithmeticOperations.round_balance(self._profit_in_currency_usd)

    @property
    def profit_in_percent_rub(self):
        self._check_profits_count()
        return ArithmeticOperations.round_balance(self._profit_in_percent_rub)

    @property
    def profit_in_percent_usd(self):
        self._check_profits_count()
        return ArithmeticOperations.round_balance(self._profit_in_percent_usd)

    @property
    def profit_invest_in_currency_rub(self):
        self._check_profits_count()
        return ArithmeticOperations.round_balance(self._profit_invest_in_currency_rub)

    @property
    def profit_invest_in_currency_usd(self):
        self._check_profits_count()
        return ArithmeticOperations.round_balance(self._profit_invest_in_currency_usd)

    @property
    def profit_invest_in_percent_rub(self):
        self._check_profits_count()
        return ArithmeticOperations.round_balance(self._profit_invest_in_percent_rub)

    @property
    def profit_invest_in_percent_usd(self):
        self._check_profits_count()
        return ArithmeticOperations.round_balance(self._profit_invest_in_percent_usd)

    @property
    def irr_rub(self):
        self._check_profits_count()
        return ArithmeticOperations.round_balance(self._irr_rub)

    @property
    def irr_usd(self):
        self._check_profits_count()
        return ArithmeticOperations.round_balance(self._irr_usd)

    def _check_profits_count(self):
        if not self.count_profits_flag:
            self.count_profits()
            self.count_profits_flag = True

    def _add_active_in_persons_portfolio(self, **kwargs):
        """Добавление актива в портфель"""
        self.add_price_in_total_and_buy_balance(**kwargs) #повторяет
        try:
            self.assets[kwargs['ident']] = Asset(usd_rub_currency=self.current_usd_rub_price, **kwargs)
        except KeyError as ex:
            logger.warning((kwargs, ex))

    def get_info_about_assets(self) -> dict:
        """Возвращает информацию об активах. Возвращает словарь активов, отсортированных по доле в портфеле
        (от самого большого)"""
        self._set_total_balance_for_assets()
        return dict(sorted(self.assets.items(), key=lambda item: item[1].percent_of_portfolio, reverse=True))

    def _set_total_balance_for_assets(self):
        for value in self.assets.values():
            value.portfolio_balance_usd = self._total_balance_in_usd




