
from .models import PersonsCrypto, PersonsTransactions
from .crypto_services import PersonsPortfolio, AssetsInfo


def add_change_in_persons_portfolio(transaction):
    persons_asset = PersonsCrypto.objects.filter(person_id=transaction.person_id, token=transaction.token_1).first()

    if not persons_asset:
        new_active = PersonsCrypto(person_id=transaction.person_id,
                                   token=transaction.token_1,
                                   size=transaction.lot if transaction.is_buy_or_sell else -transaction.lot,
                                   average_price=transaction.price)
        new_active.save()
    else:
        persons_asset.average_price = check_buy_or_sell_and_get_new_average_price(transaction, persons_asset)
        persons_asset.size += transaction.lot if transaction.is_buy_or_sell else -transaction.lot
        persons_asset.save(update_fields=['size', 'average_price'])


def add_reverse_transaction(**kwargs):
    if kwargs['token_1'].lower() == 'rub' and kwargs['token_2'].lower() == 'rub':
        return

    reverse_transaction = PersonsTransactions(person_id=kwargs['person_id'],
                                              token_1=kwargs['token_2'],
                                              token_2=kwargs['token_1'],
                                              is_buy_or_sell=not kwargs['is_buy_or_sell'],
                                              price=1/kwargs['price'],
                                              lot=kwargs['lot']*kwargs['price'])
    add_change_in_persons_portfolio(reverse_transaction)


def check_buy_or_sell_and_get_new_average_price(transaction, persons_asset):
    if transaction.is_buy_or_sell:
        return AssetsInfo.get_new_average_price(old_price=persons_asset.average_price,
                                                new_price=transaction.price,
                                                old_size=persons_asset.size,
                                                new_size=transaction.lot)
    return persons_asset.average_price
