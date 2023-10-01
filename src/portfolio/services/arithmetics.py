from typing import Union
from .config import PortfolioConfig
import logging


logger = logging.getLogger('main')


class ArithmeticOperations:

    @staticmethod
    def count_percent_profit(start_price: Union[int, float], now_price: Union[int, float]) -> float:
        """
        Считает процентное изменение стоимости с start_price до now_price актива.

        Args:
            start_price (Union[int, float]): Начальная стоимость актива.
            now_price (Union[int, float]): Текущая стоимость актива.

        Returns:
            float: Процентное изменение стоимости.
        """
        if not start_price or not now_price:
            return 0

        try:
            return (now_price / start_price - 1) * 100
        except TypeError as ex:
            logger.warning((now_price, start_price, ex))
            return 0

    @staticmethod
    def get_new_average_price(old_average_price: Union[int, float],
                              new_price: Union[int, float],
                              old_size: Union[int, float],
                              new_buy_size: Union[int, float]) -> float:
        """
        Рассчитывает новую среднюю стоимость актива.

        Args:
            old_average_price (Union[int, float]): Старая средняя стоимость актива.
            new_price (Union[int, float]): Цена новой покупки актива.
            old_size (Union[int, float]): Старый размер актива.
            new_buy_size (Union[int, float]): Размер новой покупки актива.

        Returns:
            float: Новая средняя стоимость актива.
            """
        try:
            return (old_size * old_average_price + new_buy_size * new_price) / (new_buy_size + old_size)
        except (ZeroDivisionError, TypeError) as ex:
            logger.warning((old_average_price, new_price, old_size, new_buy_size, ex))
            return 0

    @staticmethod
    def round_number(number: float, round_digit: int = PortfolioConfig.ROUND_DIGIT) -> float:
        """
        Округляет число number до указанных разрядов.

        Args:
            number (float): Число, которое нужно округлить.
            round_digit (int, optional): Количество разрядов для округления.
                Если не указано, будет использовано значение
                из PersonPortfolioConfig.ROUND_DIGIT.

        Returns:
            float: Округленное число.
        """
        return round(number, round_digit)

    @staticmethod
    def count_percent(number_1: Union[float, int], number_2: Union[float, int]) -> float:
        """
        Вычисляет процент числа number_1 от числа number_2
        :param number_1: делимое
        :param number_2: делитель
        :return: процент первого числа от второго
        """
        return number_1 / number_2 * 100

    @classmethod
    def count_rub_and_usd_price(cls, currency: str, current_price: Union[int, float], lot: Union[int, float],
                                usd_rub_currency: Union[int, float]) -> tuple[float, float]:
        """
        Возвращает текущую стоимость актива в зависимости от его валюты на
        основе еге количества и текущей цены в формате
        (стоимость в рублях, стоимость в долларах)
        :param currency:
        :param current_price:
        :param lot:
        :param usd_rub_currency:
        :return:
        """
        try:
            if cls.is_usd(currency):
                price_in_rub = current_price * lot * usd_rub_currency
                price_in_usd = current_price * lot
            else:
                price_in_rub = current_price * lot
                price_in_usd = current_price * lot / usd_rub_currency
            return price_in_rub, price_in_usd
        except (TypeError, KeyError, ZeroDivisionError) as ex:
            logger.warning(ex)

    @staticmethod
    def is_usd(currency: str) -> bool:
        """Проверяет тип валюты. Если $, то возвращает True, иначе False"""
        return currency in ('usd', 'usdt')
