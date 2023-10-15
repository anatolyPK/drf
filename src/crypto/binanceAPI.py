from functools import wraps

from dotenv import load_dotenv
from binance.client import Client
import os


load_dotenv()


def create_client(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        client = Client(api_key=os.getenv('API_KEY'), api_secret=os.getenv('SECRET_KEY'))
        return func(client, *args, **kwargs)
    return wrapper


class BinanceAPI:
    @classmethod
    def get_tickers_prices(cls, tickers: list):
        return cls.__get_price_of_ticker(tickers)

    @classmethod
    def get_historical_price(cls, tickers: list, kline: Client):
        return cls.__get_historical_klines(tickers, kline)

    @classmethod
    @create_client
    def __get_historical_klines(cls, client, tickers, kline):
        klines = client.get_historical_klines("ETHBTC", Client.KLINE_INTERVAL_1DAY, "1 Dec, 2017", "1 Jan, 2018")

    @staticmethod
    @create_client
    def __get_price_of_ticker(client, tickers: list):
        """Возвращает словарь тикер: текущая цена, а также
        курс usdt/rub"""

        tickers = [value.upper() for value in tickers]

        if 'USDTRUB' not in tickers:
            tickers.append('USDTRUB')

        tickers_and_prices = {ticker: 0 for ticker in tickers}

        values = client.get_all_tickers()
        for pair in values:
            if pair['symbol'] in tickers:
                tickers_and_prices[pair['symbol']] = float(pair['price'])
        return tickers_and_prices


