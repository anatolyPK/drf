from .crypto_services import PersonsPortfolio
from .binanceAPI import BinanceAPI


def get_portfolio(personal_assets, is_crypto: bool = True, is_get_total_balance: bool = True,
                  is_get_profit_in_currency: bool = True, is_get_profit_in_percents: bool = True,
                  is_get_assets: bool = True):
    personal_portfolio = PersonsPortfolio()

    if is_crypto:
        make_crypto_portfolio(personal_portfolio, personal_assets)
    print(24312412)
    return personal_portfolio.check_and_returns_params(is_get_total_balance,  is_get_profit_in_currency,
                                                       is_get_profit_in_percents, is_get_assets)


def make_crypto_portfolio(personal_portfolio, personal_assets):
    idents = [asset.token + 'usdt' for asset in personal_assets]
    current_prices = BinanceAPI.get_tickers_prices(idents)
    for asset in personal_assets:
        personal_portfolio.add_active(ident=asset.token,
                                      lot=asset.size,
                                      average_price_buy=asset.average_price,
                                      current_price=current_prices[asset.token.upper() + 'USDT'])