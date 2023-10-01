from datetime import datetime

from django.test import TestCase
from django.contrib.auth.models import User
from unittest import mock

from crypto.models import CryptoInvest, PersonsTransactions, PersonsCrypto
from portfolio.services.add_change_in_user_assets import TransactionHandler, AssetsChange
from stocks.models import StockInvest, UserTransaction


#
# class AddTransactionInBdTest(TestCase):
#     def test_add_transaction_in_bd(self):
#         ...
#
#
class AddInvestSummTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user1 = User.objects.create_user(username='testuser1', password='12345')
        cls.test_user1.save()

    def test_add_invest_sum_crypto(self):
        TransactionHandler.add_invest_sum(assets_type='crypto',
                                          invest_sum_in_rub=1555,
                                          invest_sum_in_usd=133,
                                          date_operation='21.03.2023',
                                          user=self.test_user1)

        new_object = CryptoInvest.objects.all().first()

        self.assertEqual(new_object.invest_sum_in_rub, 1555)
        self.assertEqual(new_object.invest_sum_in_usd, 133)
        self.assertEqual(new_object.date_operation,
                         datetime.strptime('2023-03-21', '%Y-%m-%d').date())
        self.assertEqual(new_object.user, self.test_user1)

    def test_add_invest_sum_stock(self):
        TransactionHandler.add_invest_sum(assets_type='stock',
                                          invest_sum_in_rub=1555,
                                          invest_sum_in_usd=133,
                                          date_operation='21.03.2023',
                                          user=self.test_user1)

        new_object = StockInvest.objects.all().first()

        self.assertEqual(new_object.invest_sum_in_rub, 1555)
        self.assertEqual(new_object.invest_sum_in_usd, 133)
        self.assertEqual(new_object.date_operation,
                         datetime.strptime('2023-03-21', '%Y-%m-%d').date())
        self.assertEqual(new_object.user, self.test_user1)


class AddCryptoTransaction(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.test_user1 = User.objects.create_user(username='testuser1', password='12345')
        cls.test_user1.save()

    def test_add_crypto_transaction(self):
        PersonsTransactions.objects.create(is_buy_or_sell=True,
                                           token_1='eth',
                                           token_2='usdt',
                                           lot=0.3,
                                           user=self.test_user1,
                                           price_in_rub=123456,
                                           price_in_usd=123,
                                           date_operation='2023-03-21')

        new_object = PersonsTransactions.objects.all().first()

        self.assertEqual(new_object.is_buy_or_sell, True)
        self.assertEqual(new_object.token_1, 'eth')
        self.assertEqual(new_object.token_2, 'usdt')
        self.assertEqual(new_object.lot, 0.3)
        self.assertEqual(new_object.user, self.test_user1)
        self.assertEqual(new_object.price_in_rub, 123456)
        self.assertEqual(new_object.price_in_usd, 123)
        self.assertEqual(new_object.date_operation,
                         datetime.strptime('2023-03-21', '%Y-%m-%d').date())


class AddStockTransaction(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.test_user1 = User.objects.create_user(username='testuser1', password='12345')
        cls.test_user1.save()

    def test_add_stock_transaction(self):
        UserTransaction.objects.create(is_buy_or_sell=True,
                                       figi='BBG000BN56Q9',
                                       lot=100,
                                       user=self.test_user1,
                                       price_in_rub=123456,
                                       price_in_usd=123,
                                       date_operation='2023-03-21')

        new_object = UserTransaction.objects.all().first()

        self.assertEqual(new_object.is_buy_or_sell, True)
        self.assertEqual(new_object.figi, 'BBG000BN56Q9')
        self.assertEqual(new_object.lot, 100)
        self.assertEqual(new_object.user, self.test_user1)
        self.assertEqual(new_object.price_in_rub, 123456)
        self.assertEqual(new_object.price_in_usd, 123)
        self.assertEqual(new_object.date_operation,
                         datetime.strptime('2023-03-21', '%Y-%m-%d').date())


class ChangeCryptoTransactionTest(TestCase):

    def setUp(self):
        super().setUp()

        self.test_user1 = User.objects.create_user(username='testuser1', password='12345')
        self.test_user1.save()

        PersonsTransactions.objects.create(id=9,
                                           is_buy_or_sell=True,
                                           token_1='eth',
                                           token_2='usdt',
                                           lot=100,
                                           user=self.test_user1,
                                           price_in_rub=20000,
                                           price_in_usd=150,
                                           date_operation='2023-03-21')

        PersonsTransactions.objects.create(id=10,
                                           is_buy_or_sell=True,
                                           token_1='eth',
                                           token_2='usdt',
                                           lot=100,
                                           user=self.test_user1,
                                           price_in_rub=10000,
                                           price_in_usd=150,
                                           date_operation='2023-03-21')

        PersonsCrypto.objects.create(
            user=self.test_user1,
            token='eth',
            average_price_in_rub=15000,
            average_price_in_usd=150,
            lot=200
        )

    def test_change_crypto_transaction_no_changes(self):
        old_transaction = PersonsTransactions.objects.get(id=10)

        AssetsChange.change_crypto_transaction(old_transaction)

        edited_persons_crypro = PersonsCrypto.objects.first()

        self.assertEqual(edited_persons_crypro.token, 'eth')
        self.assertEqual(edited_persons_crypro.user, self.test_user1)
        self.assertAlmostEqual(edited_persons_crypro.average_price_in_rub, 15000, delta=0.001)
        self.assertAlmostEqual(edited_persons_crypro.average_price_in_usd, 150, delta=0.001)
        self.assertEqual(edited_persons_crypro.lot, 200)

    def test_change_crypto_transaction_add_lot(self):
        old_transaction = PersonsTransactions.objects.get(id=10)
        old_transaction.lot = 200
        old_transaction.save()

        AssetsChange.change_crypto_transaction(old_transaction)

        edited_persons_crypro = PersonsCrypto.objects.first()

        self.assertEqual(edited_persons_crypro.token, 'eth')
        self.assertEqual(edited_persons_crypro.user, self.test_user1)
        self.assertAlmostEqual(edited_persons_crypro.average_price_in_rub, 13333.33333, delta=0.001)
        self.assertAlmostEqual(edited_persons_crypro.average_price_in_usd, 150, delta=0.001)
        self.assertEqual(edited_persons_crypro.lot, 300)

    def test_change_crypto_transaction_minus_lot(self):
        old_transaction = PersonsTransactions.objects.get(id=10)
        old_transaction.lot = 50
        old_transaction.save()

        AssetsChange.change_crypto_transaction(old_transaction)

        edited_persons_crypro = PersonsCrypto.objects.first()

        self.assertEqual(edited_persons_crypro.token, 'eth')
        self.assertEqual(edited_persons_crypro.user, self.test_user1)
        self.assertAlmostEqual(edited_persons_crypro.average_price_in_rub, 16667, delta=1)
        self.assertAlmostEqual(edited_persons_crypro.average_price_in_usd, 150, delta=0.001)
        self.assertEqual(edited_persons_crypro.lot, 150)

    def test_change_crypto_transaction_change_buy_or_sell(self):
        transaction = PersonsTransactions.objects.get(id=9)
        transaction.lot = 150
        transaction.save()

        old_transaction = PersonsTransactions.objects.get(id=10)
        old_transaction.is_buy_or_sell = False
        old_transaction.save()

        AssetsChange.change_crypto_transaction(old_transaction)

        edited_persons_crypro = PersonsCrypto.objects.first()

        self.assertEqual(edited_persons_crypro.token, 'eth')
        self.assertEqual(edited_persons_crypro.user, self.test_user1)
        self.assertAlmostEqual(edited_persons_crypro.average_price_in_rub, 20000, delta=0.001)
        self.assertAlmostEqual(edited_persons_crypro.average_price_in_usd, 150, delta=0.001)
        self.assertEqual(edited_persons_crypro.lot, 50)




