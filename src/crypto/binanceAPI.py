from dotenv import load_dotenv
from binance.client import Client
import os

load_dotenv()


class BinanceAPI:
    @staticmethod
    def get_tickers_prices(tickers: list):
        client = BinanceAPI.__create_client()
        return BinanceAPI.__get_price_of_ticker(client, tickers)

    @staticmethod
    def __create_client():
        client = Client(api_key=os.getenv('API_KEY'), api_secret=os.getenv('SECRET_KEY'))
        return client

    @staticmethod
    def __get_price_of_ticker(client, tickers: list):
        """Возвращает словарь тикер: текущая цена"""
        tickers = [value.upper() for value in tickers]
        symbols_and_prices = {ticker: 0 for ticker in tickers}

        values = client.get_all_tickers()
        for pair in values:
            if pair['symbol'] in tickers:
                symbols_and_prices[pair['symbol']] = float(pair['price'])
        return symbols_and_prices




