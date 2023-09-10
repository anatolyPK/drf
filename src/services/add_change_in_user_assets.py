from crypto.models import PersonsCrypto, PersonsTransactions
from stocks.models import UserStock, UserTransaction
from stocks.services.tinkoff_API import TinkoffAPI
from .portfolio import AssetsInfo
from typing import Literal, Union


class TransactionHandler:
    @classmethod
    def add_transaction_in_bd(cls, **kwargs):
        if 'token_1' not in kwargs.keys() and 'figi' not in kwargs.keys():
            raise Exception('Идентификаторы актива не переданы!')
        cls.__add_new_transaction_method[kwargs['assets_type']](**kwargs)

    @staticmethod
    def __add_stock_transaction(**kwargs):
        transaction = UserTransaction(is_buy_or_sell=kwargs['is_buy_or_sell'],
                                      figi=kwargs['figi'],
                                      lot=kwargs['lot'],
                                      user=kwargs['user'],
                                      price_in_rub=kwargs['price_in_rub'],
                                      price_in_usd=kwargs['price_in_usd'],
                                      currency=kwargs['currency'],
                                      date_operation=kwargs['date_operation'])
        transaction.save()

    @staticmethod
    def __add_crypto_transaction(**kwargs):
        transaction = PersonsTransactions(is_buy_or_sell=kwargs['is_buy_or_sell'],
                                          token_1=kwargs['token_1'],
                                          token_2=kwargs['token_2'],
                                          lot=kwargs['lot'],
                                          user=kwargs['user'],
                                          price_in_rub=kwargs['price_in_rub'],
                                          price_in_usd=kwargs['price_in_usd'],
                                          date_operation=kwargs['date_operation'])
        transaction.save()

    __add_new_transaction_method = {
        'crypto': __add_crypto_transaction,
        'stock': __add_stock_transaction,
    }

    @classmethod
    def add_reverse_transaction(cls, **kwargs):
        # if kwargs['token_1'].lower() == 'rub' and kwargs['token_2'].lower() == 'rub':
        #     return
        cls.__add_reverse_transaction_methods[kwargs['assets_type']](**kwargs)

    @staticmethod
    def __add_reverse_crypto_transaction(**kwargs):
        reverse_transaction = PersonsTransactions.objects.create(user=kwargs['user'],
                                                                 token_1=kwargs['token_2'],
                                                                 token_2=kwargs['token_1'],
                                                                 is_buy_or_sell=not kwargs['is_buy_or_sell'],
                                                                 price_in_rub=1 / kwargs['price_in_rub'],
                                                                 price_in_usd=1 / kwargs['price_in_usd'],
                                                                 lot=kwargs['lot'] * kwargs[
                                                                     'price_in_rub'])  # зачем умножать
        return {}

    @staticmethod
    def __add_reverse_stocks_transaction(**kwargs):  # продумать что изменять
        reverse_transaction = UserTransaction.objects.create(user=kwargs['user'],
                                                             figi=kwargs['figi'],
                                                             is_buy_or_sell=not kwargs['is_buy_or_sell'],
                                                             price_in_usd=1 / kwargs['price_in_usd'],
                                                             price_in_rub=1 / kwargs['price_in_rub'],
                                                             lot=kwargs['lot'] * kwargs['price_in_rub'])
        # return re

    __add_reverse_transaction_methods = {
        'crypto': __add_reverse_crypto_transaction,
        'stock': __add_reverse_stocks_transaction,
    }


class PortfolioHandler:
    @classmethod
    def update_persons_portfolio(cls, **kwargs):
        """Обновляет актив пользователя в его портфеле.
        Если актив отсутствует-добавляет его"""

        users_asset = cls.__get_user_asset(**kwargs)

        if users_asset:
            cls.__add_change_in_portfolio(users_asset=users_asset, **kwargs)
        else:
            cls.__add_new_asset_method[kwargs['assets_type']](**kwargs)

    @classmethod
    def __add_change_in_portfolio(cls, users_asset, **kwargs):
        users_asset.average_price_in_rub, users_asset.average_price_in_usd = \
            cls.__check_buy_or_sell_and_get_new_average_price(users_asset, **kwargs)
        users_asset.lot += kwargs['lot'] if kwargs['is_buy_or_sell'] else -kwargs['lot']
        users_asset.save(update_fields=['lot', 'average_price_in_rub', 'average_price_in_usd'])

    @staticmethod
    def __add_new_asset_in_crypto_portfolio(**kwargs):
        new_active = PersonsCrypto(user=kwargs['user'],
                                   token=kwargs['token_1'],
                                   lot=kwargs['lot'] if kwargs['is_buy_or_sell'] else -kwargs['lot'],
                                   average_price_in_rub=kwargs['price_in_rub'],
                                   average_price_in_usd=kwargs['price_in_usd'])
        new_active.save()

    @staticmethod
    def __add_new_asset_in_stock_portfolio(**kwargs):
        new_active = UserStock(user=kwargs['user'],
                               figi=kwargs['figi'],
                               lot=kwargs['lot'] if kwargs['is_buy_or_sell'] else -kwargs['lot'],
                               average_price_in_usd=kwargs['price_in_usd'],
                               average_price_in_rub=kwargs['price_in_rub'])
        new_active.save()

    @classmethod
    def __get_user_asset(cls, **kwargs):
        """Возвращает актив пользователя в его портфеле
        Обязательно передать user и figi (или token_1)"""
        return cls.__assets_get_methods[kwargs['assets_type']](user=kwargs['user'],
                                                               figi=kwargs['figi'],
                                                               token_1=kwargs['token_1'])

    @staticmethod
    def __get_crypto_assets(**kwargs):
        return PersonsCrypto.objects.filter(user=kwargs['user'],
                                            token=kwargs['token_1']).first()

    @staticmethod
    def __get_stock_assets(**kwargs):
        return UserStock.objects.filter(user=kwargs['user'],
                                        figi=kwargs['figi']).first()

    __assets_get_methods = {
        'crypto': __get_crypto_assets,
        'stock': __get_stock_assets
    }

    @staticmethod
    def __check_buy_or_sell_and_get_new_average_price(users_asset, **kwargs) -> tuple[float, float]:
        """Проверяет тип операции - покупка или продажа.
        Если покупка актива, то возвращает новую среднюю стоимость в виде кортежа (rub, usd).
        Если продажа - возвращает старую среднюю стоимость в виде кортежа (rub, usd)"""
        if kwargs['is_buy_or_sell']:
            return (AssetsInfo.get_new_average_price(old_price=users_asset.average_price_in_rub,
                                                     new_price=kwargs['price_in_rub'],
                                                     old_size=users_asset.lot,
                                                     new_size=kwargs['lot']),
                    AssetsInfo.get_new_average_price(old_price=users_asset.average_price_in_usd,
                                                     new_price=kwargs['price_in_usd'],
                                                     old_size=users_asset.lot,
                                                     new_size=kwargs['lot']))
        return users_asset.average_price_in_rub, users_asset.average_price_in_usd

    __add_new_asset_method = {
        'crypto': __add_new_asset_in_crypto_portfolio,
        'stock': __add_new_asset_in_stock_portfolio,
    }


class AssetsChange(TransactionHandler, PortfolioHandler):
    @classmethod
    def add_transaction_in_bd_and_update_users_assets(cls,
                                                      assets_type: Literal['crypto', 'stock'],
                                                      is_buy_or_sell: Union[bool, int],
                                                      lot: float,
                                                      user,
                                                      price_currency: float,
                                                      currency: str,
                                                      date_operation=None,
                                                      figi: str = None,
                                                      token_1: str = None,
                                                      token_2: str = None):
        price_in_rub, price_in_usd = cls.__get_rub_and_usd_price(price=price_currency, currency=currency)
        super().add_transaction_in_bd(assets_type=assets_type,
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
                                         figi=figi)
        # cls.add_reverse_transaction(assets_type=assets_type,
        #                               is_buy_or_sell=is_buy_or_sell,
        #                               lot=lot,
        #                               user=user,
        #                               price_in_rub=price_in_rub,
        #                               price_in_usd=price_in_usd,
        #                               currency=currency,
        #                               date_operation=date_operation,
        #                               token_1=token_1,
        #                               token_2=token_2,
        #                               figi=figi)

    @classmethod
    def update_persons_portfolio(cls,
                                 assets_type: Literal['crypto', 'stock'],
                                 is_buy_or_sell: bool,
                                 lot: float,
                                 user,
                                 price: float,
                                 currency: str,
                                 date_operation=None,
                                 figi: str = None,
                                 token_1: str = None,
                                 token_2: str = None):
        """Обновляет актив пользователя в его портфеле.
        Если актив отсутствует-добавляет его"""
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
                                         figi=figi)

    @classmethod
    def add_reverse_transaction(cls, **kwargs):
        super().add_reverse_transaction(**kwargs)

    @classmethod
    def __get_rub_and_usd_price(cls, price: float, currency: Literal['usd', 'usdt', 'rub']) -> tuple[..., ...]:
        """Первым аргументом возвращает цену в рублях, вторым - в долларах"""
        usd_rub_currency = TinkoffAPI.get_last_price_asset()['BBG0013HGFT4'] # figi usd/rub
        if currency in ['rub']:
            return price, round(price / usd_rub_currency, 1)
        else:
            return round(price * usd_rub_currency), price
