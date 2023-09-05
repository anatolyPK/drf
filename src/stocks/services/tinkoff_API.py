from tinkoff.invest import Client
from dotenv import load_dotenv
import os


load_dotenv()

TOKEN = os.getenv("INVEST_TOKEN")


def convert_tinkoff_money_in_currency(v):
    return v.units + v.nano / 1e9


class TinkoffAPI:
    @staticmethod
    def tinkoff_client(func):
        """Позволяет использовать данный декоратор вместо
        with Client(TOKEN) as client"""
        def wrapper(*args, **kwargs):
            with Client(TOKEN) as client:
                return func(client=client, *args, **kwargs)
        return wrapper

    @classmethod
    @tinkoff_client
    def get_last_price_asset(cls, client, figi: list[str]) -> dict[str: float]:
        """Возвращает котировки переданных активов, а также usd/rub"""
        figi.append('BBG0013HGFT4') #usd/rub
        assets = client.market_data.get_last_prices(figi=figi)
        return {asset.figi: convert_tinkoff_money_in_currency(asset.price) for asset in assets.last_prices}

    @classmethod
    @tinkoff_client
    def get_actual_tinkoff_shares(cls, client):
        return client.instruments.shares()

    @classmethod
    @tinkoff_client
    def get_actual_tinkoff_bonds(cls, client):
        return client.instruments.bonds()

    @classmethod
    @tinkoff_client
    def get_actual_tinkoff_etfs(cls, client):
        return client.instruments.etfs()

    @classmethod
    @tinkoff_client
    def get_actual_tinkoff_currencies(cls, client):
        return client.instruments.currencies()
