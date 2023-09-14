from datetime import datetime, timedelta

from tinkoff.invest import Client
from tinkoff.invest.grpc.marketdata_pb2 import CANDLE_INTERVAL_4_HOUR, CANDLE_INTERVAL_30_MIN
from dotenv import load_dotenv
import os
import logging


load_dotenv()
TOKEN = os.getenv("INVEST_TOKEN")

logger = logging.getLogger('main')


USD_RUB_FIGI = 'BBG0013HGFT4'


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
    def get_last_price_asset(cls, client, *, figi: list[str] = None) -> dict[str: float]:
        """Возвращает котировки переданных активов, а также usd/rub.
        Без аргументов возвращает usd/rub"""
        if figi is None:
            figi = list()
        figi.append(USD_RUB_FIGI)  # usd/rub
        assets = client.market_data.get_last_prices(figi=figi)
        return {asset.figi: convert_tinkoff_money_in_currency(asset.price) for asset in assets.last_prices}

    @classmethod
    @tinkoff_client
    def get_price_on_chosen_date(cls, client, *, date: datetime, figi: str = USD_RUB_FIGI):
        try:
            prices = client.market_data.get_candles(figi=figi,
                                                    from_=date - timedelta(days=2),
                                                    to=date,
                                                    interval=CANDLE_INTERVAL_30_MIN)
            return convert_tinkoff_money_in_currency(prices.candles[-1].close)
        except IndexError as ex:
            logger.warning(ex)
            return 0

        # //TODO если выходные - то ошибка

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
