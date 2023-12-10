from crypto.models import PersonsCrypto, PersonsTransactions, CryptoInvest
from stocks.models import StockInvest, Share, Bond, Etf, Currency, UserShare, UserCurrency, \
    UserBond, UserEtf, UserShareTransaction, UserBondTransaction, UserCurrencyTransaction, UserEtfTransaction


class Stock:
    pass


class Crypto:
    pass


class PortfolioConfig:
    # параметр, который идет в метод 'round'
    ROUND_DIGIT = 1
    ROUND_DIGIT_LOT = 4

    USD_RUB_FIGI = 'BBG0013HGFT4'

    users_models = {
        'crypto': PersonsCrypto,
        'stock': {
            'share': UserShare,
            'bond': UserBond,
            'currency': UserCurrency,
            'etf': UserEtf,
        }
    }

    _users_transactions_models = {
        'crypto': PersonsTransactions,
        'stock': {
            'share': UserShareTransaction,
            'bond': UserBondTransaction,
            'currency': UserCurrencyTransaction,
            'etf': UserEtfTransaction,
        }
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