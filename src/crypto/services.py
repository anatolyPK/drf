import django.db.models
from .models import PersonsCrypto, PersonsTransactions
from .crypto_services import PersonsPortfolio, get_new_average_price
from .binanceAPI import BinanceAPI


def get_portfolio(user_id, is_crypto: bool = True,
                  is_get_total_balance: bool = True,
                  is_get_profit_in_currency: bool = True,
                  is_get_profit_in_percents: bool = True,
                  is_get_assets: bool = True):

    personal_portfolio = PersonsPortfolio()

    if is_crypto:
        personal_assets = PersonsCrypto.objects.all().filter(person_id=user_id)
        make_crypto_portfolio(personal_portfolio, personal_assets)

    return personal_portfolio.check_and_returns_params(is_get_total_balance,  is_get_profit_in_currency,
                                                       is_get_profit_in_percents, is_get_assets)


def make_crypto_portfolio(personal_portfolio: PersonsPortfolio, personal_assets: django.db.models.QuerySet):
    idents = [asset.token + 'usdt' for asset in personal_assets]
    current_prices = BinanceAPI.get_tickers_prices(idents)
    for asset in personal_assets:
        personal_portfolio.add_active_in_persons_portfolio(ident=asset.token,
                                                           lot=asset.size,
                                                           average_price_buy=asset.average_price,
                                                           current_price=current_prices[asset.token.upper() + 'USDT'])


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
        return get_new_average_price(old_price=persons_asset.average_price,
                                     new_price=transaction.price,
                                     old_size=persons_asset.size,
                                     new_size=transaction.lot)
    return persons_asset.average_price
