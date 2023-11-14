import time
from functools import wraps
from typing import Literal
from datetime import datetime

from dotenv import load_dotenv
from binance.client import Client
import os, sys
import logging

# from tasks import get_historical_klines


logger_debug = logging.getLogger('debug')


load_dotenv()


client = Client(api_key=os.getenv('API_KEY'), api_secret=os.getenv('SECRET_KEY'))


class HistoricalPrice:
    _1DAYS_KLINE = Client.KLINE_INTERVAL_15MINUTE
    _1WEEKS_KLINE = Client.KLINE_INTERVAL_1HOUR
    _1MONTH_KLINE = Client.KLINE_INTERVAL_1DAY
    _1YEAR_KLINE = Client.KLINE_INTERVAL_3DAY
    _ALL_TIME_KLINE = Client.KLINE_INTERVAL_1WEEK

    @classmethod
    def get_historical_price(cls, tickers: list, period: Literal['daily', 'weekly', 'monthly', 'yearly', 'all']):
        tickers_prices = {}
        for ticker_pair in tickers:
            tickers_prices[ticker_pair] = cls.convert_klines_list(cls._get_klines(ticker_pair, period))
        return tickers_prices

    @classmethod
    def _get_klines(cls, ticker_pair, period):
        klines = {
            'daily': cls.get_daily_klines,
            'weekly': cls.get_weekly_klines,
            'monthly': cls.get_monthly_klines,
            'yearly': cls.get_yearly_klines,
            'all': cls.get_all_time_klines
        }

        if period not in klines:
            raise ValueError(f"Unsupported assets_type: {period}")

        historical_klines = klines[period](ticker_pair)
        return historical_klines

    @classmethod
    def get_daily_klines(cls, pair):
        # get_historical_klines.delay(pair)
        return client.get_historical_klines(pair, cls._1DAYS_KLINE, "1 day ago")

    @classmethod
    def get_weekly_klines(cls, pair):
        return client.get_historical_klines(pair, cls._1WEEKS_KLINE, "1 week ago")

    @classmethod
    def get_monthly_klines(cls, pair):
        return client.get_historical_klines(pair, cls._1MONTH_KLINE, "1 month ago")

    @classmethod
    def get_yearly_klines(cls, pair):
        return client.get_historical_klines(pair, cls._1YEAR_KLINE, "1 year ago")

    @classmethod
    def get_all_time_klines(cls, pair):
        return client.get_historical_klines(pair, cls._ALL_TIME_KLINE)

    @classmethod
    def convert_klines_list(cls, klines):
        return [(datetime.fromtimestamp(int(kline[0] / 1000)), float(kline[4])) for kline in klines]


class BinanceAPI:
    @staticmethod
    # //TODO как лучше хранить или запрашивать историю портфеля
    def get_historical_price(tickers: list, period: Literal['daily', 'weekly', 'monthly', 'yearly', 'all']):
        return HistoricalPrice.get_historical_price(tickers, period)

    @staticmethod
    def get_all_tickers_prices():
        return client.get_all_tickers()

# all_size = []
#
# tickers_count = len([x['symbol'] for x in BinanceAPI.get_all_tickers_prices() if x['symbol'].endswith('USDT')])
# logger_debug.debug(f'len - {tickers_count}')
# size_1 = sys.getsizeof(BinanceAPI.get_historical_price(['ETHUSDT'], 'daily'))
# time.sleep(0.2)
# size_2 = sys.getsizeof(BinanceAPI.get_historical_price(['ETHUSDT'], 'weekly'))
# time.sleep(0.2)
# size_3 = sys.getsizeof(BinanceAPI.get_historical_price(['ETHUSDT'], 'monthly'))
# time.sleep(0.2)
# size_4 = sys.getsizeof(BinanceAPI.get_historical_price(['ETHUSDT'], 'yearly'))
# time.sleep(0.2)
# size_5 = sys.getsizeof(BinanceAPI.get_historical_price(['ETHUSDT'], 'all'))
#
#
# logger_debug.debug((size_1+size_2+size_3+size_4+size_5)*tickers_count)
