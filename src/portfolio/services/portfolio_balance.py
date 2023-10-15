from django.contrib.auth.models import User
from django.utils import timezone

from datetime import timedelta
from datetime import datetime

from crypto.models import CryptoPortfolioBalance
from .config import PortfolioConfig
from .portfolio import PortfolioMaker

import logging


logger_debug = logging.getLogger('debug')


def write_in_db_portfolio_balance():
    #медленно работает
    current_time = timezone.now()
    now_datetime = current_time.replace(second=00, microsecond=00)

    users = User.objects.all()

    for assets_type, db in PortfolioConfig.users_models.items():
        for user in users:
            assets = db.objects.filter(user=user)

            if not assets:
                continue

            portfolio_maker = PortfolioMaker(assets_type=assets_type, user=user, assets=assets)

            portfolio_info = portfolio_maker.portfolio.get_info_about_portfolio()

            balance_in_rub = portfolio_info['total_balance_in_rub']
            balance_in_usd = portfolio_info['total_balance_in_usd']

            CryptoPortfolioBalance.objects.create(user=user,
                                                  portfolio_type=assets_type,
                                                  sum_in_rub=balance_in_rub,
                                                  sum_in_usd=balance_in_usd,
                                                  date=now_datetime)


class BalanceGetter:
    @staticmethod
    #каждые 5 минут
    def get_daily_portfolio_balance(user: User):
        one_day_ago = timezone.now() - timedelta(days=1)
        return CryptoPortfolioBalance.objects.filter(user=user, date__gte=one_day_ago)

    @staticmethod
    def get_weekly_15_min_portfolio_balance(user: User):
        one_week_ago = timezone.now() - timedelta(weeks=1)

        balance_list = []

        current_time = one_week_ago.replace(minute=0, second=0, microsecond=0)
        end_time = timezone.now().replace(minute=0, second=0, microsecond=0)

        while current_time <= end_time:
            balance = CryptoPortfolioBalance.objects.filter(user=user, date=current_time)
            balance_list.extend(balance)

            current_time += timedelta(minutes=15)

        return balance_list

    @staticmethod
    def get_monthly_hourly_portfolio_balance(user: User):
        one_week_ago = timezone.now() - timedelta(days=30)

        balance_list = []

        current_time = one_week_ago.replace(minute=0, second=0, microsecond=0)
        end_time = timezone.now().replace(minute=0, second=0, microsecond=0)

        while current_time <= end_time:
            balance = CryptoPortfolioBalance.objects.filter(user=user, date=current_time)
            balance_list.extend(balance)

            current_time += timedelta(hours=1)

        return balance_list

    @staticmethod
    def get_yearly_daily_portfolio_balance(user: User):
        one_week_ago = timezone.now() - timedelta(days=360)

        balance_list = []

        current_time = one_week_ago.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

        while current_time <= end_time:
            balance = CryptoPortfolioBalance.objects.filter(user=user, date=current_time)
            balance_list.extend(balance)

            current_time += timedelta(days=1)

        return balance_list

    #написать тесты и через них реализовывть!!


class BalanceDeleter:
    @classmethod
    def delete_old_balance(cls):
        balance_queryset = CryptoPortfolioBalance.objects.all()
        now_datetime = timezone.now()

        for balance in balance_queryset:
            if cls._should_delete_balance(date=balance.date, now_datetime=now_datetime):
                balance.delete()

    @classmethod
    def _should_delete_balance(cls, date: datetime, now_datetime: datetime):
        logger_debug.debug(f'{date} {cls._check_daily(date, now_datetime)} {cls._check_weekly(date, now_datetime)} '
                           f'{cls._check_monthly(date, now_datetime)} {cls._check_yearly(date, now_datetime)}')
        return (
                cls._check_daily(date, now_datetime) and
                cls._check_weekly(date, now_datetime) and
                cls._check_monthly(date, now_datetime) and
                cls._check_yearly(date, now_datetime)
        )

    @staticmethod
    def _check_elapsed_days(date: datetime, now_datetime: datetime, days: int):
        return (now_datetime - date).days >= days

    @classmethod
    def _check_daily(cls, date: datetime, now_datetime: datetime):
        return (
                cls._check_elapsed_days(date, now_datetime, 1) or
                date.minute % 5 != 0
        )

    @classmethod
    def _check_weekly(cls, date: datetime, now_datetime: datetime):
        return (
            cls._check_elapsed_days(date, now_datetime, 7) or
            date.minute not in (0, 15, 30, 45)
        )

    @classmethod
    def _check_monthly(cls, date: datetime, now_datetime: datetime):
        return (
            cls._check_elapsed_days(date, now_datetime, 30) or
            date.minute != 0
        )

    @classmethod
    def _check_yearly(cls, date: datetime, now_datetime: datetime):
        return (
            cls._check_elapsed_days(date, now_datetime, 360) or
            (date.minute != 0 or date.hour != 0)
        )

