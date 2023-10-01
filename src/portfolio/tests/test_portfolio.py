# from django.test import TestCase
# from django.contrib.auth.models import User
# from unittest import mock
#
# from crypto.models import PersonsCrypto
# from portfolio.services.portfolio import CryptoPortfolio, ArithmeticOperations, PersonPortfolioConfig, PortfolioBalance
# from stocks.models import UserStock, Share, Bond, Etf, Currency
#
# import logging
#
#
# logger_debug = logging.getLogger('debug')
#
#
# class CountPercentProfitTest(TestCase):
#     def test_count_percent_profit_correct_value(self):
#         values_1 = ((100, 150), 50.0)
#         values_2 = ((200, 100), -50.0)
#         for values in values_1, values_2:
#             profit = ArithmeticOperations.count_percent_profit(*values[0])
#             self.assertEqual(profit, values[1])
#
#     def test_count_percent_profit_incorrect_value(self):
#         values_1 = ((0, 150), 0)
#         values_2 = ((150, 0), 0)
#         for values in values_1, values_2:
#             profit = ArithmeticOperations.count_percent_profit(*values[0])
#             self.assertEqual(profit, values[1])
#
#     def test_count_percent_profit_incorrect_types(self):
#         values_1 = ((None, 150), 0)
#         values_2 = ((150, '33'), 0)
#         values_3 = (([150], 33), 0)
#         for values in values_1, values_2, values_3:
#             profit = ArithmeticOperations.count_percent_profit(*values[0])
#             self.assertEqual(profit, values[1])
#
#
# class GetNewAveragePriceTest(TestCase):
#     def test_get_new_average_price_correct_value(self):
#         old_average_price, new_price = 100, 200
#         old_size, new_buy_size = 10, 10
#         new_av_price = ArithmeticOperations.get_new_average_price(old_average_price=old_average_price,
#                                                                   new_price=new_price,
#                                                                   old_size=old_size,
#                                                                   new_buy_size=new_buy_size)
#         self.assertEqual(new_av_price, 150)
#
#         old_average_price, new_price = 333, 21
#         old_size, new_buy_size = 0.2, 32
#         new_av_price = ArithmeticOperations.get_new_average_price(old_average_price=old_average_price,
#                                                                   new_price=new_price,
#                                                                   old_size=old_size,
#                                                                   new_buy_size=new_buy_size)
#         self.assertEqual(round(new_av_price, 1), 22.9)
#
#     def test_get_new_average_price_incorrect_value(self):
#         old_average_price, new_price = 100, 200
#         old_size, new_buy_size = 0, 0
#         new_av_price = ArithmeticOperations.get_new_average_price(old_average_price=old_average_price,
#                                                                   new_price=new_price,
#                                                                   old_size=old_size,
#                                                                   new_buy_size=new_buy_size)
#         self.assertEqual(new_av_price, 0)
#
#         old_average_price, new_price = 333, 0
#         old_size, new_buy_size = 0.2, 32
#         new_av_price = ArithmeticOperations.get_new_average_price(old_average_price=old_average_price,
#                                                                   new_price=new_price,
#                                                                   old_size=old_size,
#                                                                   new_buy_size=new_buy_size)
#         self.assertEqual(round(new_av_price, 1), 2.1)
#
#     def test_get_new_average_price_incorrect_types(self):
#         old_average_price, new_price = None, 200
#         old_size, new_buy_size = 3, 1
#         new_av_price = ArithmeticOperations.get_new_average_price(old_average_price=old_average_price,
#                                                                   new_price=new_price,
#                                                                   old_size=old_size,
#                                                                   new_buy_size=new_buy_size)
#         self.assertEqual(new_av_price, 0)
#
#         old_average_price, new_price = 3, 200
#         old_size, new_buy_size = [3], 25
#         new_av_price = ArithmeticOperations.get_new_average_price(old_average_price=old_average_price,
#                                                                   new_price=new_price,
#                                                                   old_size=old_size,
#                                                                   new_buy_size=new_buy_size)
#         self.assertEqual(new_av_price, 0)
#
#
# class AddPlusIfMoreThanZeroTest(TestCase):
#     def test_add_plus_if_more_than_zero_with_positive_integer(self):
#         value_1 = ArithmeticOperations.add_plus_if_more_than_zero(3)
#         value_2 = ArithmeticOperations.add_plus_if_more_than_zero(103)
#         self.assertEqual(value_1, '+3')
#         self.assertEqual(value_2, '+103')
#
#     def test_add_plus_if_more_than_zero_with_negative_integer(self):
#         value_1 = ArithmeticOperations.add_plus_if_more_than_zero(-3)
#         value_2 = ArithmeticOperations.add_plus_if_more_than_zero(-356)
#         self.assertEqual(value_1, '-3')
#         self.assertEqual(value_2, '-356')
#
#     def test_add_plus_if_more_than_zero_with_zero(self):
#         value = ArithmeticOperations.add_plus_if_more_than_zero(0)
#         self.assertEqual(value, '0')
#
#     def test_add_plus_if_more_than_zero_with_another_type(self):
#         value_1 = ArithmeticOperations.add_plus_if_more_than_zero('3')
#         value_2 = ArithmeticOperations.add_plus_if_more_than_zero([2])
#         value_3 = ArithmeticOperations.add_plus_if_more_than_zero({'key': 'value'})
#         value_4 = ArithmeticOperations.add_plus_if_more_than_zero(None)
#         self.assertEqual(value_1, None)
#         self.assertEqual(value_2, None)
#         self.assertEqual(value_3, None)
#         self.assertEqual(value_4, None)
#
#
# class UsersModelsNameTest(TestCase):
#     def test_users_crypto_models(self):
#         self.assertEqual(PersonPortfolioConfig._users_models['crypto'], PersonsCrypto)
#
#     def test_users_stock_models(self):
#         self.assertEqual(PersonPortfolioConfig._users_models['stock'], UserStock)
#
#
# class ModelsForShareBondsEtfsCurrencies(TestCase):
#     def test_share_models(self):
#         self.assertEqual(PersonPortfolioConfig._models_for_shares_bonds_etfs_currencies['shares'], Share)
#
#     def test_bonds_models(self):
#         self.assertEqual(PersonPortfolioConfig._models_for_shares_bonds_etfs_currencies['bonds'], Bond)
#
#     def test_etfs_models(self):
#         self.assertEqual(PersonPortfolioConfig._models_for_shares_bonds_etfs_currencies['etfs'], Etf)
#
#     def test_currencies_models(self):
#         self.assertEqual(PersonPortfolioConfig._models_for_shares_bonds_etfs_currencies['currencies'], Currency)
#
#
# class AddPriceInTotalAndBuyBalanceTest(TestCase):
#     def test_add_price_in_total_and_buy_balance(self):
#         test_user1 = User.objects.create_user(username='testuser1', password='12345')
#         test_user1.save()
#
#         portfolio_balance = PortfolioBalance(user=test_user1, type_of_assets='crypto')
#         portfolio_balance._current_usd_rub_price = 100
#         kwargs = {
#             'currency': 'usd',
#             'current_price': 25000.0,
#             'lot': 0.5,
#             'average_price_buy_in_rub': 100,
#             'average_price_buy_in_usd': 20000
#         }
#         portfolio_balance._add_price_in_total_and_buy_balance(**kwargs)
#
#         self.assertEqual(portfolio_balance._total_balance_in_rub, 25000*0.5 *100)
#         self.assertEqual(portfolio_balance._total_balance_in_usd, 25000*0.5)
#         self.assertEqual(portfolio_balance._buy_price_in_rub, 100 * 0.5)
#         self.assertEqual(portfolio_balance._buy_price_in_usd, 20000*0.5)
#
#
#
#
#
#
#
#
#
#
#
#
#
#
# class GetInfoAboutPortfolioTestCase(TestCase):
#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()
#         cls.ROUND_DIGIT = 1
#
#         cls.test_user1 = User.objects.create_user(username='testuser1', password='12345')
#         cls.test_user1.save()
#
#         PersonsCrypto.objects.create(token='eth',
#                                      lot=0.3,
#                                      average_price_in_rub=20000,
#                                      average_price_in_usd=1000,
#                                      user=cls.test_user1)
#
#         UserStock.objects.create(figi='BBG0025Y4RY4',
#                                  lot=1,
#                                  average_price_in_rub=1000,
#                                  average_price_in_usd=100,
#                                  user=cls.test_user1)
#
#     def setUp(self):
#         self.fake_price = {'ETHUSDT': 1500.0,
#                            'USDTRUB': 100}
#         self.patcher = mock.patch('crypto.binanceAPI.BinanceAPI.get_tickers_prices')
#         self.MockClass = self.patcher.start()
#         self.MockClass.return_value = self.fake_price
#
#     def tearDown(self):
#         self.patcher.stop()
#
#     def test_get_info_about_crypto_portfolio(self):
#         crypto_asset = PersonsCrypto.objects.filter(token='eth')
#         logger_debug.debug(crypto_asset)
#         data = {'total_balance_in_rub': 45000.0,
#                 'total_balance_in_usd': 450,
#                 'buy_price_in_rub': 20000,
#                 'buy_price_in_usd': 1000,
#                 'profit_in_percents_rub': round(ArithmeticOperations.count_percent_profit(
#                     20000 * crypto_asset.lot, 1500 * 100 * crypto_asset.lot), self.ROUND_DIGIT),
#                 'profit_in_percents_usd': round(ArithmeticOperations.count_percent_profit(
#                     1000 * crypto_asset.lot, 1500 * crypto_asset.lot), self.ROUND_DIGIT),
#                 'profit_in_currency_rub': round(45000 - 20000 * crypto_asset.lot, self.ROUND_DIGIT),
#                 'profit_in_currency_usd': round(450 - 1000 * crypto_asset.lot, self.ROUND_DIGIT),
#                 'usd_rub_currency': 100}
#
#         test_crypto = CryptoPortfolio(user=self.test_user1, assets=crypto_asset)
#         self.assertEqual(test_crypto.get_info_about_portfolio()['total_balance_in_rub'],
#                          crypto_asset.lot * self.fake_price['ETHUSDT'] * self.fake_price['USDTRUB'])
#         self.assertEqual(test_crypto.get_info_about_portfolio()['total_balance_in_usd'],
#                          crypto_asset.lot * self.fake_price['ETHUSDT'])
#         self.assertEqual(test_crypto.get_info_about_portfolio()['buy_price_in_rub'],
#                          crypto_asset.average_price_in_rub * crypto_asset.lot)
#         self.assertEqual(test_crypto.get_info_about_portfolio()['profit_in_percents_rub'],
#                          ArithmeticOperations.add_plus_if_more_than_zero(
#                              round(ArithmeticOperations.count_percent_profit(crypto_asset.average_price_in_rub
#                                                                              * crypto_asset.lot,
#                                                                              self.fake_price['ETHUSDT']
#                                                                              * self.fake_price['USDTRUB']
#                                                                              * crypto_asset.lot),
#                                    self.ROUND_DIGIT)))
#         self.assertEqual(test_crypto.get_info_about_portfolio()['profit_in_percents_usd'],
#                          ArithmeticOperations.add_plus_if_more_than_zero(
#                              round(ArithmeticOperations.count_percent_profit(crypto_asset.average_price_in_usd
#                                                                              * crypto_asset.lot,
#                                                                              self.fake_price['ETHUSDT']
#                                                                              * crypto_asset.lot),
#                                    self.ROUND_DIGIT)))
#
#     def test_get_info_about_stock_portfolio(self):
#         ...
