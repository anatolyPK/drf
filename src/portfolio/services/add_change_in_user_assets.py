from datetime import datetime

from stocks.services.tinkoff_API import TinkoffAPI
from portfolio.services.portfolio import AssetsInfo, PersonPortfolioConfig
from typing import Literal, Union
import logging

logger = logging.getLogger('main')
logger_debug = logging.getLogger('debug')


class TransactionHandler(PersonPortfolioConfig):
    @classmethod
    def add_transaction_in_bd(cls, **kwargs):
        try:
            cls._add_new_transaction(**kwargs)
        except KeyError as ex:
            logger.warning(ex)

    @classmethod
    def add_invest_sum(cls, **kwargs):
        try:
            new_invest = PersonPortfolioConfig._users_invest_sum_models[kwargs['assets_type']](
                invest_sum_in_rub=kwargs['invest_sum_in_rub'],
                invest_sum_in_usd=kwargs['invest_sum_in_usd'],
                date_operation=cls.__refactor_date(kwargs['date_operation']),
                user=kwargs['user'])

            new_invest.save()
        except KeyError as ex:
            logger.warning(ex)

    @staticmethod
    def _add_stock_transaction(**kwargs):
        try:
            transaction = TransactionHandler._users_transactions_models[kwargs['assets_type']] \
                (is_buy_or_sell=kwargs['is_buy_or_sell'],
                 figi=kwargs['figi'],
                 lot=kwargs['lot'],
                 user=kwargs['user'],
                 price_in_rub=kwargs['price_in_rub'],
                 price_in_usd=kwargs['price_in_usd'],
                 currency=kwargs['currency'],
                 date_operation=TransactionHandler.
                 __refactor_date(kwargs['date_operation']))
            transaction.save()
        except KeyError as ex:
            logger.warning(ex)

    @staticmethod
    def _add_crypto_transaction(**kwargs):
        try:
            transaction = TransactionHandler._users_transactions_models[kwargs['assets_type']] \
                (is_buy_or_sell=kwargs['is_buy_or_sell'],
                 token_1=kwargs['token_1'],
                 token_2=kwargs['token_2'],
                 lot=kwargs['lot'],
                 user=kwargs['user'],
                 price_in_rub=kwargs['price_in_rub'],
                 price_in_usd=kwargs['price_in_usd'],
                 date_operation=TransactionHandler.
                 __refactor_date(kwargs['date_operation']))
            transaction.save()
        except KeyError as ex:
            logger.warning(ex)
        except TypeError as ex:
            logger.warning(ex)

    @staticmethod
    def __refactor_date(date):
        try:
            date_in_dt_format = datetime.strptime(date, '%d.%m.%Y')
            return date_in_dt_format.strftime('%Y-%m-%d')
        except TypeError as ex:
            logger.warning(ex)
        except ValueError as ex:
            logger.warning(ex)

    @classmethod
    def _add_new_transaction(cls, assets_type: str, **kwargs):
        transaction_methods = {
            'crypto': cls._add_crypto_transaction,
            'stock': cls._add_stock_transaction,
        }
        if assets_type in transaction_methods:
            transaction_methods[assets_type](**kwargs)
        else:
            logger.warning(f"Unsupported asset type: {assets_type}")


class PortfolioHandler(PersonPortfolioConfig):
    @classmethod
    def update_persons_portfolio(cls, **kwargs):
        """Обновляет актив пользователя в его портфеле.
        Если актив отсутствует-добавляет его"""

        users_asset = cls.__get_user_asset(**kwargs)
        try:
            if users_asset:
                cls.__add_change_in_portfolio(users_asset=users_asset, **kwargs)
            else:
                cls.__add_new_asset_method[kwargs['assets_type']](**kwargs)
        except KeyError as ex:
            logger.warning(ex)

    @classmethod
    def __add_change_in_portfolio(cls, users_asset, **kwargs):
        try:
            if kwargs['token_1'] not in ('usdt', 'busd'):
                users_asset.average_price_in_rub, users_asset.average_price_in_usd = \
                    cls.__check_buy_or_sell_and_get_new_average_price(users_asset, **kwargs)
            users_asset.lot += kwargs['lot'] if kwargs['is_buy_or_sell'] else -kwargs['lot']
            users_asset.save(update_fields=['lot', 'average_price_in_rub', 'average_price_in_usd'])

        except KeyError as ex:
            logger.warning(ex)
        except ValueError as ex:
            logger.warning(ex)
        except AttributeError as ex:
            logger.warning(ex)

    @staticmethod
    def __add_new_asset_in_crypto_portfolio(**kwargs):
        try:
            new_active = PortfolioHandler._users_models[kwargs['assets_type']](user=kwargs['user'],
                                                                               token=kwargs['token_1'],
                                                                               lot=kwargs['lot'] if kwargs[
                                                                                   'is_buy_or_sell'] else -kwargs[
                                                                                   'lot'],
                                                                               average_price_in_rub=kwargs[
                                                                                   'price_in_rub'],
                                                                               average_price_in_usd=kwargs[
                                                                                   'price_in_usd'])
            new_active.save()
        except AttributeError as ex:
            logger.warning(ex)
        except KeyError as ex:
            logger.warning(ex)

    @staticmethod
    def __add_new_asset_in_stock_portfolio(**kwargs):
        try:
            new_active = PortfolioHandler._users_models[kwargs['assets_type']](user=kwargs['user'],
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

    @classmethod
    def __get_user_asset(cls, **kwargs):
        """Возвращает актив пользователя в его портфеле.
        Обязательно передать user и figi (или token_1)"""
        try:
            return cls.__assets_get_methods[kwargs['assets_type']](assets_type=kwargs['assets_type'],
                                                                   user=kwargs['user'],
                                                                   figi=kwargs['figi'],
                                                                   token_1=kwargs['token_1'])
        except KeyError as ex:
            logger.warning(ex)

    # // TODO reverse for usdt/rub
    @staticmethod
    def __get_crypto_assets(**kwargs):
        logger.info(kwargs['assets_type'])
        try:
            return PortfolioHandler._users_models[kwargs['assets_type']].objects.filter(user=kwargs['user'],
                                                                                        token=kwargs['token_1']).first()
        except KeyError as ex:
            logger.warning(ex)
        except NameError as ex:
            logger.warning(ex)
        #     //TODO заменить названия БД на методы

    @staticmethod
    def __get_stock_assets(**kwargs):
        try:
            return PortfolioHandler._users_models[kwargs['assets_type']].objects.filter(user=kwargs['user'],
                                                                                        figi=kwargs['figi']).first()
        except KeyError as ex:
            logger.warning(ex)
        except NameError as ex:
            logger.warning(ex)

    __assets_get_methods = {
        'crypto': __get_crypto_assets,
        'stock': __get_stock_assets
    }

    @staticmethod
    def __check_buy_or_sell_and_get_new_average_price(users_asset, **kwargs) -> tuple[float, float]:
        """Проверяет тип операции - покупка или продажа.
        Если покупка актива, то возвращает новую среднюю стоимость в виде кортежа (average_rub, average_usd).
        Если продажа - возвращает старую среднюю стоимость в виде кортежа (average_rub, average_usd)"""
        try:
            if kwargs['is_buy_or_sell']:
                return (AssetsInfo.get_new_average_price(old_average_price=users_asset.average_price_in_rub,
                                                         new_price=kwargs['price_in_rub'],
                                                         old_size=users_asset.lot,
                                                         new_buy_size=kwargs['lot']),
                        AssetsInfo.get_new_average_price(old_average_price=users_asset.average_price_in_usd,
                                                         new_price=kwargs['price_in_usd'],
                                                         old_size=users_asset.lot,
                                                         new_buy_size=kwargs['lot']))
            return users_asset.average_price_in_rub, users_asset.average_price_in_usd
        except KeyError as ex:
            logger.warning(ex)

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
                                                      currency: Literal['rub', 'usd', 'usdt'],
                                                      date_operation=None,
                                                      figi: str = None,
                                                      token_1: str = None,
                                                      token_2: str = None):

        price_in_rub, price_in_usd = cls.__get_rub_and_usd_price(date_operation=date_operation,
                                                                 price=price_currency,
                                                                 currency=currency,
                                                                 token_1=token_1)
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
                                 user,
                                 price_in_rub: float,
                                 price_in_usd: float,
                                 currency: str,
                                 date_operation=None,
                                 figi: str = None,
                                 token_1: str = None,
                                 token_2: str = None,
                                 is_transaction_update: bool = False):
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
                                         figi=figi,
                                         is_transaction_update=is_transaction_update)

    @classmethod
    def add_reverse_transaction(cls, **kwargs):
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
        except KeyError as ex:
            logger.warning(ex)
        except ZeroDivisionError as ex:
            logger.warning(ex)

    @classmethod
    def __get_rub_and_usd_price(cls,
                                date_operation: str,
                                price: float,
                                currency: Literal['usd', 'usdt', 'rub'],
                                token_1: any) -> tuple[..., ...]:
        """Первым аргументом возвращает цену в рублях, вторым - в долларах."""

        try:
            usd_rub_currency = TinkoffAPI.get_price_on_chosen_date(
                date=datetime.strptime(date_operation, '%d.%m.%Y'))

            if token_1 in ('usd', 'usdc', 'usdt', 'busd'):
                return price, 1
            elif currency in ('rub'):
                return price, price / usd_rub_currency
            else:
                return price * usd_rub_currency, price

        except TypeError as ex:
            logger.warning(ex)
        except ZeroDivisionError as ex:
            logger.warning(ex)
        except ValueError as ex:
            logger.warning(ex)

    @classmethod
    def add_invest_sum(cls,
                       user,
                       assets_type: Literal['crypto', 'stock'],
                       invest_sum_in_usd: float or int,
                       invest_sum_in_rub: float or int,
                       date_operation: str):

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
    def change_crypto_transaction(cls, transaction):
        logger_debug.debug(transaction)
        token_transactions = cls._users_transactions_models['crypto'].objects.filter(token_1=transaction.token_1)

        for transaction in token_transactions:
            cls.update_persons_portfolio(assets_type='crypto',
                                         is_buy_or_sell=transaction.is_buy_or_sell,
                                         lot=transaction.lot,
                                         user=transaction.user,
                                         price_in_rub=transaction.price_in_rub,
                                         price_in_usd=transaction.price_in_usd,
                                         currency='usd',
                                         date_operation=transaction.date_operation,
                                         token_1=transaction.token_1,
                                         token_2=transaction.token_2,
                                         )

# //TODO изменение на 5% за сутки
