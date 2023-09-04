from crypto.models import PersonsCrypto
from stocks.models import UserStock
from .portfolio import AssetsInfo


class PersonsPortfolio:

    @classmethod
    def update_persons_portfolio(cls, transaction, assets_type: str):
        """assets_type принимает значение crypto или stock"""
        users_asset = cls.__get_user_asset(transaction, assets_type)
        if users_asset:
            cls.__add_change_in_portfolio(users_asset, transaction)
        else:
            cls.__add_new_asset_method[assets_type](transaction)

    @classmethod
    def __add_change_in_portfolio(cls, users_asset, transaction):
        users_asset.average_price = cls.__check_buy_or_sell_and_get_new_average_price(transaction, users_asset)
        users_asset.lot += transaction.lot if transaction.is_buy_or_sell else -transaction.lot
        users_asset.save(update_fields=['lot', 'average_price'])

    @staticmethod
    def __add_new_asset_in_crypto_portfolio(transaction):
        new_active = PersonsCrypto(user=transaction.user,
                                   token=transaction.token_1,
                                   lot=transaction.lot if transaction.is_buy_or_sell else -transaction.lot,
                                   average_price=transaction.price)
        new_active.save()

    @staticmethod
    def __add_new_asset_in_stock_portfolio(transaction):
        new_active = UserStock(user=transaction.user,
                               figi=transaction.figi,
                               lot=transaction.lot if transaction.is_buy_or_sell else -transaction.lot,
                               average_price=transaction.price)
        new_active.save()

    @staticmethod
    def __get_user_asset(transaction, assets_type: str):
        """Возвращает выбранный актив пользователя.
        Если отсутствует - False"""

        if assets_type == 'crypto':
            persons_asset = PersonsCrypto.objects.filter(user=transaction.user, token=transaction.token_1).first()
        elif assets_type == 'stock':
            persons_asset = UserStock.objects.filter(user=transaction.user, figi=transaction.figi).first()
        else:
            raise Exception(f'wrong {assets_type}')

        return persons_asset

    @staticmethod
    def __check_buy_or_sell_and_get_new_average_price(transaction, persons_asset):
        if transaction.is_buy_or_sell:
            return AssetsInfo.get_new_average_price(old_price=persons_asset.average_price,
                                                    new_price=transaction.price,
                                                    old_size=persons_asset.lot,
                                                    new_size=transaction.lot)
        return persons_asset.average_price

    __add_new_asset_method = {
        'crypto': __add_new_asset_in_crypto_portfolio,
        'stock': __add_new_asset_in_stock_portfolio,
    }
