from crypto.models import PersonsCrypto, PersonsTransactions, CryptoInvest
from stocks.models import UserStock, UserTransaction, StockInvest, Share, Bond, Etf, Currency


class PortfolioConfig:
    # параметр, который идет в метод 'round'
    ROUND_DIGIT = 1
    ROUND_DIGIT_LOT = 4

    USD_RUB_FIGI = 'BBG0013HGFT4'

    users_models = {
        'crypto': PersonsCrypto,
        'stock': UserStock
    }

    _users_transactions_models = {
        'crypto': PersonsTransactions,
        'stock': UserTransaction
    }

    _users_invest_sum_models = {
        'crypto': CryptoInvest,
        'stock': StockInvest
    }
    _models_for_shares_bonds_etfs_currencies = {
        'shares': Share,
        'bonds': Bond,
        'etfs': Etf,
        'currencies': Currency
    }