# from django.test import TestCase
# from crypto.binanceAPI import BinanceAPI
#
#
# class GetTickerPricesTestCase(TestCase):
#     def test_get_prices(self):
#         tickers = ['btcusdt']
#         result = BinanceAPI.get_tickers_prices(tickers)
#         prices = {
#             'USDTRUB': 98.51,
#             'BTCUSDT': 25826
#         }
#         self.assertEqual(prices, result)
#
#     def test_get_prices_with_usdtrub(self):
#         tickers = ['usdtrub', 'btcusdt']
#         result = BinanceAPI.get_tickers_prices(tickers)
#         prices = {
#             'USDTRUB': 98.51,
#             'BTCUSDT': 25826
#         }
#         self.assertEqual(prices, result)
