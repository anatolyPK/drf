
from .models import PersonsTransactions
from services.portfolio import PersonsPortfolio
from services.add_change_in_user_assets import AssetsChange


def add_reverse_transaction(**kwargs):
    if kwargs['token_1'].lower() == 'rub' and kwargs['token_2'].lower() == 'rub':
        return

    reverse_transaction = PersonsTransactions(user=kwargs['user'],
                                              token_1=kwargs['token_2'],
                                              token_2=kwargs['token_1'],
                                              is_buy_or_sell=not kwargs['is_buy_or_sell'],
                                              price=1/kwargs['price'],
                                              lot=kwargs['lot']*kwargs['price'])

    AssetsChange.update_persons_portfolio(transaction=reverse_transaction,
                                            assets_type='crypto')



