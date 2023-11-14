import time
from datetime import datetime
from typing import Literal, Union, Tuple

from django.contrib.auth.models import User
from django.db import transaction

from stocks.services.tinkoff_API import TinkoffAPI
from .arithmetics import ArithmeticOperations
from .config import PortfolioConfig

import logging

logger = logging.getLogger('main')
logger_debug = logging.getLogger('debug')


class TransactionHandler(PortfolioConfig):
    @classmethod
    def add_invest_sum(cls,
                       assets_type: Literal['crypto', 'stock'],
                       invest_sum_in_rub: Union[float, int],
                       invest_sum_in_usd: Union[float, int],
                       user: User,
                       date_operation: str) -> None:
        """
        Добавляет сумму инвестирования в базу данных.

        :param assets_type: Тип актива ('crypto' или 'stock').
        :param invest_sum_in_rub: Сумма инвестирования в рублях.
        :param invest_sum_in_usd: Сумма инвестирования в долларах.
        :param user: Пользователь, для которого добавляется сумма.
        :param date_operation: Дата операции.
        """
        try:
            new_invest = cls._users_invest_sum_models[assets_type](
                invest_sum_in_rub=invest_sum_in_rub,
                invest_sum_in_usd=invest_sum_in_usd,
                date_operation=cls._refactor_date(date_operation),
                user=user
            )
            new_invest.save()
        except KeyError as ex:
            logger.warning(ex)

    @classmethod
    def add_transaction_in_bd(cls,
                              assets_type: Literal['crypto', 'stock'],
                              **kwargs) -> None:
        """
        Добавляет транзакцию в базу данных.

        :param assets_type: Тип актива ('crypto' или 'stock').
        - is_buy_or_sell (bool): Указывает, является ли транзакция покупкой (True) или продажей (False).
        - figi (str): Уникальный идентификатор актива (FIGI).
        - token_1 (str): Токен первого актива, например, "BTC".
        - token_2 (str): Токен второго актива, например, "USDT".
        - lot (float): Количество активов в транзакции.
        - user (User): Пользователь, выполнивший транзакцию (объект модели User).
        - price_in_rub (float): Цена транзакции в рублях.
        - price_in_usd (float): Цена транзакции в долларах.
        - date_operation (str): Дата и время проведения транзакции в формате строки.
        """
        transaction_methods = {
            'crypto': cls._add_crypto_transaction,
            'stock': cls._add_stock_transaction,
        }
        if assets_type in transaction_methods:
            transaction_methods[assets_type](assets_type=assets_type, **kwargs)
        else:
            logger.warning(f"Unsupported asset type: {assets_type}")

    @staticmethod
    def _add_crypto_transaction(**kwargs) -> None:
        """
        Добавляет транзакцию с криптовалютным активом в базу данных.

        :param kwargs: Словарь с параметрами транзакции.
        """
        try:
            transaction = (TransactionHandler._users_transactions_models[kwargs['assets_type']]
                           (is_buy_or_sell=kwargs['is_buy_or_sell'],
                            token_1=kwargs['token_1'],
                            token_2=kwargs['token_2'],
                            lot=kwargs['lot'],
                            user=kwargs['user'],
                            price_in_rub=kwargs['price_in_rub'],
                            price_in_usd=kwargs['price_in_usd'],
                            date_operation=TransactionHandler._refactor_date(kwargs['date_operation'])))
            transaction.save()
        except (KeyError, TypeError) as ex:
            logger.warning((kwargs, ex))

    @staticmethod
    def _add_stock_transaction(**kwargs) -> None:
        """
        Добавляет транзакцию с акциями в базу данных.

        :param kwargs: Словарь с параметрами транзакции.
        """
        try:
            transaction = (TransactionHandler._users_transactions_models[kwargs['assets_type']]
                           (is_buy_or_sell=kwargs['is_buy_or_sell'],
                            figi=kwargs['figi'],
                            lot=kwargs['lot'],
                            user=kwargs['user'],
                            price_in_rub=kwargs['price_in_rub'],
                            price_in_usd=kwargs['price_in_usd'],
                            currency=kwargs['currency'],
                            date_operation=TransactionHandler.
                            _refactor_date(kwargs['date_operation'])))
            transaction.save()
        except KeyError as ex:
            logger.warning(ex)

    @staticmethod
    def _refactor_date(date: str) -> str:
        """
        Преобразует дату из одного формата в другой.

        :param date: Дата в формате строки (например, '25.09.2023').
        :return: Дата в формате строки 'YYYY-MM-DD' (например, '2023-09-25').
        """
        try:
            date_in_dt_format = datetime.strptime(date, '%d.%m.%Y')
            return date_in_dt_format.strftime('%Y-%m-%d')
        except (TypeError, ValueError) as ex:
            logger.warning((date, ex))


class PortfolioHandler(PortfolioConfig):
    @classmethod
    def update_persons_portfolio(cls, **kwargs):
        """
        Обновляет актив пользователя в его портфеле.
        Если актив отсутствует-добавляет его
        """
        users_asset = cls._get_user_asset(**kwargs)
        try:
            if users_asset:
                cls._add_change_in_portfolio(users_asset=users_asset, **kwargs)
            else:
                cls._add_new_asset(**kwargs)
        except KeyError as ex:
            logger.warning(ex)

    @classmethod
    def _get_user_asset(cls, assets_type: str, **kwargs):
        """
        Возвращает актив пользователя в его портфеле.
        Обязательно передать user и figi (или token_1)
        """
        assets_get_methods = {
            'crypto': cls._get_crypto_assets,
            'stock': cls._get_stock_assets
        }
        if assets_type in assets_get_methods:
            return assets_get_methods[assets_type](assets_type=assets_type, **kwargs)
        else:
            logger.warning(f"Unsupported asset type: {assets_type}")

    @staticmethod
    def _get_crypto_assets(**kwargs):
        try:
            return PortfolioHandler.users_models[kwargs['assets_type']].objects.filter(user=kwargs['user'],
                                                                                       token=kwargs['token_1']).first()
        except (KeyError, NameError) as ex:
            logger.warning((kwargs, ex))

    @staticmethod
    def _get_stock_assets(**kwargs):
        try:
            return PortfolioHandler.users_models[kwargs['assets_type']].objects.filter(user=kwargs['user'],
                                                                                       figi=kwargs['figi']).first()
        except (KeyError, NameError) as ex:
            logger.warning((kwargs, ex))

    @classmethod
    def _add_change_in_portfolio(cls, users_asset, **kwargs):
        try:
            if kwargs['token_1'] not in ('usdt', 'busd'):
                users_asset.average_price_in_rub, users_asset.average_price_in_usd = \
                    cls._check_buy_or_sell_and_get_new_average_price(users_asset, **kwargs)
            users_asset.lot += kwargs['lot'] if kwargs['is_buy_or_sell'] else -kwargs['lot']
            users_asset.save(update_fields=['lot', 'average_price_in_rub', 'average_price_in_usd'])

        except (KeyError, ValueError, AttributeError) as ex:
            logger.warning((users_asset, kwargs, ex))

    @staticmethod
    def _add_new_asset_in_crypto_portfolio(**kwargs):
        try:
            new_active = PortfolioConfig.users_models[kwargs['assets_type']](user=kwargs['user'],
                                                                             token=kwargs['token_1'],
                                                                             lot=kwargs['lot'] if kwargs[
                                                                                 'is_buy_or_sell'] else -kwargs[
                                                                                 'lot'],
                                                                             average_price_in_rub=kwargs[
                                                                                 'price_in_rub'],
                                                                             average_price_in_usd=kwargs[
                                                                                 'price_in_usd'])
            new_active.save()
        except (AttributeError, KeyError) as ex:
            logger.warning((kwargs, ex))

    @staticmethod
    def _add_new_asset_in_stock_portfolio(**kwargs):
        try:
            new_active = PortfolioConfig.users_models[kwargs['assets_type']](user=kwargs['user'],
                                                                             figi=kwargs['figi'],
                                                                             lot=kwargs['lot'] if kwargs[
                                                                                 'is_buy_or_sell'] else -kwargs[
                                                                                 'lot'],
                                                                             average_price_in_usd=kwargs[
                                                                                 'price_in_usd'],
                                                                             average_price_in_rub=kwargs[
                                                                                 'price_in_rub'])
            new_active.save()
        except AttributeError as ex:
            logger.warning(ex)

    @staticmethod
    def _check_buy_or_sell_and_get_new_average_price(users_asset, **kwargs) -> tuple[float, float]:
        """
        Проверяет тип операции - покупка или продажа.
        Если покупка актива, то возвращает новую среднюю стоимость в виде кортежа (average_rub, average_usd).
        Если продажа - возвращает старую среднюю стоимость в виде кортежа (average_rub, average_usd)
        """
        try:
            if kwargs['is_buy_or_sell']:
                return (ArithmeticOperations.get_new_average_price(old_average_price=users_asset.average_price_in_rub,
                                                                   new_price=kwargs['price_in_rub'],
                                                                   old_size=users_asset.lot,
                                                                   new_buy_size=kwargs['lot']),
                        ArithmeticOperations.get_new_average_price(old_average_price=users_asset.average_price_in_usd,
                                                                   new_price=kwargs['price_in_usd'],
                                                                   old_size=users_asset.lot,
                                                                   new_buy_size=kwargs['lot']))
            return users_asset.average_price_in_rub, users_asset.average_price_in_usd
        except KeyError as ex:
            logger.warning(ex)

    @classmethod
    def _add_new_asset(cls, **kwargs):
        _add_new_asset_method = {
            'crypto': cls._add_new_asset_in_crypto_portfolio,
            'stock': cls._add_new_asset_in_stock_portfolio,
        }
        assets_type = kwargs['assets_type']
        if assets_type in _add_new_asset_method:
            _add_new_asset_method[assets_type](**kwargs)
        else:
            logger.warning(f"Unsupported asset type: {assets_type}")


class AssetsChange(TransactionHandler, PortfolioHandler):
    @classmethod
    def add_transaction_in_bd_and_update_users_assets(cls,
                                                      assets_type: Literal['crypto', 'stock'],
                                                      is_buy_or_sell: Union[bool, int],
                                                      lot: float,
                                                      user: User,
                                                      price_currency: float,
                                                      currency: Literal['rub', 'usd', 'usdt'],
                                                      date_operation=None,
                                                      figi: str = None,
                                                      token_1: str = None,
                                                      token_2: str = None):
        """
        Добавляет транзакцию в базу данных и обновляет портфель пользователя.

        :param assets_type: Тип активов ('crypto' или 'stock').
        :param is_buy_or_sell: Признак покупки (True) или продажи (False).
        :param lot: Количество активов.
        :param user: Пользователь.
        :param price_currency: Цена актива в выбранной валюте.
        :param currency: Валюта ('rub', 'usd', 'usdt').
        :param date_operation: Дата операции (строка в формате 'dd.mm.yyyy').
        :param figi: ФИГИ актива (для 'stock').
        :param token_1: Токен актива (для 'crypto').
        :param token_2: Дополнительный токен актива (для 'crypto').
        """
        price_in_rub, price_in_usd = cls._get_rub_and_usd_price(date_operation=date_operation,
                                                                price=price_currency,
                                                                currency=currency,
                                                                token_1=token_1)
        cls.add_transaction_in_bd(assets_type=assets_type,
                                  is_buy_or_sell=is_buy_or_sell,
                                  lot=lot,
                                  user=user,
                                  price_in_rub=price_in_rub,
                                  price_in_usd=price_in_usd,
                                  currency=currency,
                                  date_operation=date_operation,
                                  token_1=token_1,
                                  token_2=token_2,
                                  figi=figi)

        cls.update_persons_portfolio(assets_type=assets_type,
                                     is_buy_or_sell=is_buy_or_sell,
                                     lot=lot,
                                     user=user,
                                     price_in_rub=price_in_rub,
                                     price_in_usd=price_in_usd,
                                     currency=currency,
                                     date_operation=date_operation,
                                     token_1=token_1,
                                     token_2=token_2,
                                     figi=figi)

        if assets_type == 'crypto' and token_1 not in ('rub', 'usdt', 'usdc', 'busd') and token_1 != 'rub':
            cls.add_reverse_transaction(assets_type=assets_type,
                                        is_buy_or_sell=is_buy_or_sell,
                                        lot=lot,
                                        user=user,
                                        price_in_rub=price_in_rub,
                                        price_in_usd=price_in_usd,
                                        currency=currency,
                                        date_operation=date_operation,
                                        token_1=token_1,
                                        token_2=token_2,
                                        figi=figi)

    @classmethod
    def update_persons_portfolio(cls,
                                 assets_type: Literal['crypto', 'stock'],
                                 is_buy_or_sell: bool,
                                 lot: float,
                                 user: User,
                                 price_in_rub: float,
                                 price_in_usd: float,
                                 currency: str,
                                 date_operation=None,
                                 figi: str = None,
                                 token_1: str = None,
                                 token_2: str = None,
                                 is_transaction_update: bool = False):
        """
        Обновляет актив пользователя в его портфеле.
        Если актив отсутствует-добавляет его

        :param assets_type: Тип активов ('crypto' или 'stock').
        :param is_buy_or_sell: Признак покупки (True) или продажи (False).
        :param lot: Количество активов.
        :param user: Пользователь.
        :param price_in_rub: Цена актива в рублях.
        :param price_in_usd: Цена актива в долларах.
        :param currency: Валюта ('rub', 'usd', 'usdt').
        :param date_operation: Дата операции (строка в формате 'dd.mm.yyyy').
        :param figi: ФИГИ актива (для 'stock').
        :param token_1: Токен актива (для 'crypto').
        :param token_2: Дополнительный токен актива (для 'crypto').
        :param is_transaction_update: Признак обновления по транзакции.
        """

        super().update_persons_portfolio(assets_type=assets_type,
                                         is_buy_or_sell=is_buy_or_sell,
                                         lot=lot,
                                         user=user,
                                         price_in_rub=price_in_rub,
                                         price_in_usd=price_in_usd,
                                         currency=currency,
                                         date_operation=date_operation,
                                         token_1=token_1,
                                         token_2=token_2,
                                         figi=figi,
                                         is_transaction_update=is_transaction_update)

    @classmethod
    def add_reverse_transaction(cls, **kwargs):
        """
        Добавляет обратную транзакцию и обновляет портфель пользователя.

        :param kwargs: Параметры транзакции (см. add_transaction_in_bd_and_update_users_assets).
        """
        try:
            super().update_persons_portfolio(assets_type=kwargs['assets_type'],
                                             is_buy_or_sell=not kwargs['is_buy_or_sell'],
                                             lot=kwargs['lot'] * kwargs['price_in_usd'],
                                             user=kwargs['user'],
                                             price_in_rub=1 / kwargs['price_in_rub'],
                                             price_in_usd=1 / kwargs['price_in_usd'],
                                             currency='rub' if kwargs['token_1'] == 'rub' else kwargs['currency'],
                                             date_operation=kwargs['date_operation'],
                                             token_1=kwargs['token_2'],
                                             token_2=kwargs['token_1'],
                                             figi=kwargs['figi'])
        except (KeyError, ZeroDivisionError) as ex:
            logger.warning(f"{ex} - {kwargs}")

    @classmethod
    def _get_rub_and_usd_price(cls,
                               date_operation: str,
                               price: float,
                               currency: Literal['usd', 'usdt', 'rub'],
                               token_1: any) -> Tuple[float, float]:
        """
        Возвращает цену актива в рублях и долларах на основе выбранной валюты.

        :param date_operation: Дата операции (строка в формате 'dd.mm.yyyy').
        :param price: Цена актива в выбранной валюте.
        :param currency: Валюта ('usd', 'usdt', 'rub').
        :param token_1: Токен актива.

        :return: Кортеж из двух значений - цена актива в рублях и цена актива в долларах.
        """

        try:
            usd_rub_currency = TinkoffAPI.get_price_on_chosen_date(
                date=datetime.strptime(date_operation, '%d.%m.%Y'))

            if token_1 in ('usd', 'usdc', 'usdt', 'busd'):
                return price, 1
            elif currency in ('rub'):
                return price, price / usd_rub_currency
            else:
                return price * usd_rub_currency, price

        except (TypeError, ZeroDivisionError, ValueError) as ex:
            logger.warning(f'{ex}')

    @classmethod
    def add_invest_sum(cls,
                       user: User,
                       assets_type: Literal['crypto', 'stock'],
                       invest_sum_in_usd: float or int,
                       invest_sum_in_rub: float or int,
                       date_operation: str) -> None:
        """
        Добавляет сумму инвестиций в базу данных и обновляет портфель пользователя.

        :param user: Пользователь.
        :param assets_type: Тип активов ('crypto' или 'stock').
        :param invest_sum_in_usd: Сумма инвестиций в долларах.
        :param invest_sum_in_rub: Сумма инвестиций в рублях.
        :param date_operation: Дата операции (строка в формате 'dd.mm.yyyy').
        """

        super().add_invest_sum(invest_sum_in_rub=invest_sum_in_rub,
                               invest_sum_in_usd=invest_sum_in_usd,
                               date_operation=date_operation,
                               user=user,
                               assets_type=assets_type)

        cls.update_persons_portfolio(assets_type=assets_type,
                                     is_buy_or_sell=True,
                                     lot=invest_sum_in_usd,
                                     user=user,
                                     price_in_rub=invest_sum_in_rub / invest_sum_in_usd,
                                     price_in_usd=1,
                                     currency='usd',
                                     date_operation=date_operation,
                                     token_1='usdt'
                                     )

    @classmethod
    def change_crypto_transaction(cls, changed_transaction):
        """
        Изменяет транзакции с криптовалютами и обновляет портфель пользователя.

        :param changed_transaction: Транзакция для изменения.
        """
        cls.users_models['crypto'].objects.filter(token=changed_transaction.token_1).delete()

        token_transactions = cls._users_transactions_models['crypto'].objects.filter(
            token_1=changed_transaction.token_1,
            user=changed_transaction.user
        )

        for changed_transaction in token_transactions:
            cls.update_persons_portfolio(assets_type='crypto',
                                         is_buy_or_sell=changed_transaction.is_buy_or_sell,
                                         lot=changed_transaction.lot,
                                         user=changed_transaction.user,
                                         price_in_rub=changed_transaction.price_in_rub,
                                         price_in_usd=changed_transaction.price_in_usd,
                                         currency='usd',
                                         date_operation=changed_transaction.date_operation,
                                         token_1=changed_transaction.token_1,
                                         token_2=changed_transaction.token_2,
                                         )
# //TODO изменение на 5% за сутки
# //TODO разбить класс на мелкие классы
