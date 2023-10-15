from datetime import timedelta
from unittest import TestCase

from django.contrib.auth.models import User
from django.utils import timezone

from crypto.models import CryptoPortfolioBalance
from portfolio.services.portfolio_balance import BalanceGetter, BalanceDeleter


class BalanceGetterTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        current_time = timezone.now()
        now_datetime = current_time.replace(minute=00, second=00, microsecond=00)

        datetime_dct = {
            'hour_ago': now_datetime - timedelta(hours=1),
            '10_min_ago': now_datetime - timedelta(minutes=10),
            'hour_and_8_min_ago': now_datetime - timedelta(hours=1, minutes=8),
            'day_ado': now_datetime - timedelta(days=1),
            'day_ado_and_hour_ago': now_datetime - timedelta(days=1, hours=1),
            'day_ado_and_hour_and_8_min_ago': now_datetime - timedelta(days=1, hours=1, minutes=8),
            '2_days_ago': now_datetime - timedelta(days=2),
            '2_days_and_30_min_ago': now_datetime - timedelta(days=2, minutes=30),
            'week_ago': now_datetime - timedelta(weeks=1),
            'month_ago': now_datetime - timedelta(days=30),
            'month_and_hour_ago': now_datetime - timedelta(days=30, hours=1),
            '2_month_ago': now_datetime - timedelta(days=60),
        }

        cls.test_user1 = User.objects.create_user(username='testuser1', password='12345')
        cls.test_user1.save()

        for date in datetime_dct.values():
            CryptoPortfolioBalance.objects.create(user=cls.test_user1,
                                                  portfolio_type='crypto',
                                                  sum_in_rub=10000,
                                                  sum_in_usd=1000,
                                                  date=date)

    def test_get_daily_portfolio_balance(self):
        balance_queryset = BalanceGetter.get_daily_portfolio_balance(user=self.test_user1)

        self.assertEqual(len(balance_queryset), 3)

    def test_get_weekly_15_min_portfolio_balance(self):
        balance_queryset = BalanceGetter.get_weekly_15_min_portfolio_balance(user=self.test_user1)

        self.assertEqual(len(balance_queryset), 6)

    def test_get_monthly_hourly_portfolio_balance(self):
        balance_queryset = BalanceGetter.get_monthly_hourly_portfolio_balance(user=self.test_user1)

        self.assertEqual(len(balance_queryset), 6)

    @classmethod
    def tearDownClass(cls) -> None:
        CryptoPortfolioBalance.objects.filter(user=cls.test_user1).delete()
        User.objects.filter(username='testuser1').delete()


class BalanceDeletterTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        current_time = timezone.now()
        now_datetime = current_time.replace(minute=00, second=00, microsecond=00)

        datetime_dct = {
            'hour_ago': now_datetime - timedelta(hours=1),
            '10_min_ago': now_datetime - timedelta(minutes=10),
            'hour_and_8_min_ago': now_datetime - timedelta(hours=1, minutes=8), #del
            'day_ado': now_datetime - timedelta(days=1),
            'day_ado_and_hour_ago': now_datetime - timedelta(days=1, hours=1),
            'day_ado_and_hour_and_8_min_ago': now_datetime - timedelta(days=1, hours=1, minutes=8), #del
            '2_days_ago': now_datetime - timedelta(days=2),
            '2_days_and_30_min_ago': now_datetime - timedelta(days=2, minutes=30),
            'week_ago': now_datetime - timedelta(weeks=1),
            'month_ago': now_datetime - timedelta(days=30), #del
            'month_and_hour_ago': now_datetime - timedelta(days=30, hours=1), #del
            '2_month_ago': now_datetime - timedelta(days=60), #del
        }

        cls.test_user1 = User.objects.create_user(username='testuser1', password='12345')
        cls.test_user1.save()

        for date in datetime_dct.values():
            CryptoPortfolioBalance.objects.create(user=cls.test_user1,
                                                  portfolio_type='crypto',
                                                  sum_in_rub=10000,
                                                  sum_in_usd=1000,
                                                  date=date)

    def test_delete_old_balance(self):
        BalanceDeleter.delete_old_balance()
        queryset = CryptoPortfolioBalance.objects.all()
        self.assertEqual(len(queryset), 7)

        #УДАЛЯТЬ ЗАПСИСИ ПОСЛЕ ТЕСТОВ!!!

    @classmethod
    def tearDownClass(cls) -> None:
        User.objects.filter(username='testuser1').delete()
        CryptoPortfolioBalance.objects.filter(user=cls.test_user1).delete()