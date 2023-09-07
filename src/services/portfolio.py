from crypto.binanceAPI import BinanceAPI
from crypto.models import PersonsCrypto
from stocks.models import UserStock, Share, Bond, Etf, Currency
from stocks.services.tinkoff_API import TinkoffAPI


class PersonPortfolioConfig:
    def __init__(self, user, type_of_assets):
        self._total_balance_in_rub = 0
        self._buy_price_in_rub = 0
        self._current_usd_rub_price = 0
        self._tickers = {}
        self._type_of_assets = type_of_assets
        self._user = user

    USD_RUB_FIGI = 'BBG0013HGFT4'

    _models_name = {
        'crypto': PersonsCrypto,
        'stock': UserStock
    }

    _models_name_for_shares_bonds_etfs_currencies = {
        'shares': Share,
        'bonds': Bond,
        'etfs': Etf,
        'currencies': Currency
    }


class PortfolioBalance(PersonPortfolioConfig):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _add_price_in_total_and_buy_balance(self, current_price, lot, currency,
                                            average_price_buy_in_rub, average_price_buy_in_usd):
        self._add_price_in_total_balance(current_price=current_price,
                                         lot=lot,
                                         currency=currency)
        self._add_price_in_buy_price(average_price_in_rub=average_price_buy_in_rub,
                                     lot=lot,
                                     currency=currency)

    def _add_price_in_total_balance(self, current_price, lot, currency):
        if self._check_currency_is_usd(currency):
            self._total_balance_in_rub += current_price * lot * self._current_usd_rub_price
        else:
            self._total_balance_in_rub += current_price * lot

    def _add_price_in_buy_price(self, average_price_in_rub, lot, currency):
        if self._check_currency_is_usd(currency):
            self._buy_price_in_rub += average_price_in_rub * lot * self._current_usd_rub_price
        else:
            self._buy_price_in_rub += average_price_in_rub * lot

    @staticmethod
    def _check_currency_is_usd(currency):
        """Проверяет тип валюты. Если $, то возвращает True, иначе False"""
        if currency in ('usd', 'usdt'):
            return True
        return False

    @staticmethod
    def _check_crypto_currency(token: str):
        if token.lower() == 'rub':
            return 'rub'
        return 'usd'

    def _set_usdt_rub_currency(self, current_prices=None, now_currency_usd_rub=None):
        if not current_prices and not now_currency_usd_rub:
            raise Exception("Проверьте переданные данные!")

        elif now_currency_usd_rub:
            self._current_usd_rub_price = now_currency_usd_rub
        else:
            self._current_usd_rub_price = current_prices['USDTRUB']


class PersonsPortfolioDB(PortfolioBalance):
    def _get_datas_from_model(self):
        return self._models_name[self._type_of_assets].objects.all().filter(user=self._user)


class PersonsPortfolio(PersonsPortfolioDB):
    """Класс для работы с портфелем пользователя."""
    def __init__(self, *, type_of_assets: str, user):
        super().__init__(type_of_assets=type_of_assets,
                         user=user)

    def _add_active_in_persons_portfolio(self, ident: str, lot: float, average_price_buy_in_rub: float, current_price: float,
                                         currency: str, average_price_buy_in_usd: float, name):
        """Добавление актива в портфель"""
        self._add_price_in_total_and_buy_balance(current_price=current_price,
                                                 lot=lot,
                                                 currency=currency,
                                                 average_price_buy_in_rub=average_price_buy_in_rub,
                                                 average_price_buy_in_usd=average_price_buy_in_usd)

        self._tickers[ident] = AssetsInfo(ident=ident,
                                          lot=lot,
                                          average_price_buy_in_rub=average_price_buy_in_rub,
                                          average_price_buy_in_usd=average_price_buy_in_usd,
                                          current_price=current_price,
                                          currency=currency,
                                          name=name)

    def get_info_about_portfolio_and_assets(self) -> dict:
        """Возвращает информацию о портфеле, а также об активах."""
        portfolios_info = self.get_info_about_portfolio()
        portfolios_info['assets'] = self.get_info_about_assets()
        return portfolios_info

    def get_info_about_portfolio(self) -> dict:
        """Возвращает информацию о портфеле"""
        params_dict = {'total_balance_in_rub': round(self._total_balance_in_rub),
                       'total_balance_in_usd': round(self._total_balance_in_rub * self._current_usd_rub_price),
                       'buy_price': self._buy_price_in_rub,
                       'profit_in_percents': AssetsInfo.count_percent_profit(self._buy_price_in_rub,
                                                                             self._total_balance_in_rub),
                       'profit_in_currency': round(self._total_balance_in_rub - self._buy_price_in_rub, 1),
                       'usd_rub_currency': round(self._current_usd_rub_price, 1)}
        return params_dict

    def get_info_about_assets(self) -> dict:
        """Возвращает информацию об активах."""
        tickers_info = {}

        for ticker in self._tickers:
            tickers_info[ticker] = {}
            tickers_info[ticker]['name'] = self._tickers[ticker].name
            tickers_info[ticker]['lot'] = self._tickers[ticker].lot
            tickers_info[ticker]['average_price_buy'] = self._tickers[ticker].average_price_buy_in_rub
            tickers_info[ticker]['current_price'] = self._tickers[ticker].current_price
            tickers_info[ticker]['currency'] = self._get_currency(self._tickers[ticker].currency)
            tickers_info[ticker]['profit_in_currency'] = self._tickers[ticker].profit_in_currency
            tickers_info[ticker]['profit_in_percent'] = self._tickers[ticker].profit_in_percent
            tickers_info[ticker]['total_now_balance'] = round(self._tickers[ticker].total_now_balance, 1)

        return tickers_info

    def _get_currency(self, currency):
        if currency.lower() in ('usd', 'usdt'):
            return '$'
        elif currency.lower() == 'rub':
            return '₽'


class CryptoPortfolio(PersonsPortfolio):
    def __init__(self, user):
        super().__init__(type_of_assets='crypto', user=user)
        self.__make_portfolio()

    def __make_portfolio(self):
        personal_assets = self._get_datas_from_model()
        tokens = self._get_tokens_for_binance_api(personal_assets)
        current_prices_of_assets = BinanceAPI.get_tickers_prices(tokens)
        self._set_usdt_rub_currency(current_prices_of_assets)
        for asset in personal_assets:
            self._add_active_in_persons_portfolio(ident=asset.token,
                                                  lot=asset.lot,
                                                  average_price_buy_in_rub=asset.average_price,
                                                  current_price=self._get_current_price(current_prices_of_assets,
                                                                                        asset),
                                                  currency=self._check_crypto_currency(asset.token),
                                                  name=asset.token)

    @staticmethod
    def _get_tokens_for_binance_api(personal_assets):
        tokens = []
        for asset in personal_assets:
            if asset.token == 'rub':
                tokens.append('usdt' + asset.token)
            else:
                tokens.append(asset.token + 'usdt')
        return tokens

    @staticmethod
    def _get_current_price(current_prices, asset):
        if asset.token == 'rub':
            return 1
        elif asset.token == 'usdt':
            return current_prices['USDTRUB'] #если не будет юсдт, то ошибка будет
        try:
            return current_prices[asset.token.upper() + 'USDT']
        except Exception as ex:
            print(ex)


class StockPortfolio(PersonsPortfolio):
    def __init__(self, user):
        super().__init__(type_of_assets='stock', user=user)
        self.__make_portfolio()

    def __make_portfolio(self):
        personal_assets = self._get_datas_from_model()
        figis = [asset.figi for asset in personal_assets]
        currencies, names = self._get_currencies_and_names_from_bd(figis)
        current_prices_of_assets = TinkoffAPI.get_last_price_asset(figi=figis)

        self._set_usdt_rub_currency(now_currency_usd_rub=current_prices_of_assets[self.USD_RUB_FIGI])

        for asset in personal_assets:
            self._add_active_in_persons_portfolio(ident=asset.figi,
                                                  lot=asset.lot,
                                                  average_price_buy_in_rub=asset.average_price_in_rub,
                                                  average_price_buy_in_usd=asset.average_price_in_usd,
                                                  current_price=current_prices_of_assets[asset.figi],
                                                  currency=currencies[asset.figi],
                                                  name=names[asset.figi])

    def _get_currencies_and_names_from_bd(self, figis):
        currencies, names = {}, {}
        for db_name in self._models_name_for_shares_bonds_etfs_currencies.values():
            try:
                assets_from_bd = db_name.objects.all().filter(figi__in=figis)
                for asset in assets_from_bd:
                    currencies[asset.figi] = asset.currency
                    names[asset.figi] = asset.name
                continue
            except KeyError:
                pass
        return currencies, names


class AssetsInfo:
    """Класс для получения данных о значениях конкретного актива"""
    def __init__(self, ident: str, lot, average_price_buy_in_rub, average_price_buy_in_usd, current_price, currency, name):
        self.ident = ident
        self.name = name
        self.lot = lot
        self.average_price_buy_in_rub = average_price_buy_in_rub
        self.average_price_buy_in_usd = average_price_buy_in_usd
        self.current_price = current_price
        self.currency = currency
        self.total_now_balance = self.current_price * self.lot
        self.profit_in_percent = self.__count_percent_from_average_to_current_price()
        self.profit_in_currency = round(self.total_now_balance - self.average_price_buy_in_rub * self.lot, 2)

    def __count_percent_from_average_to_current_price(self):
        return self.count_percent_profit(self.average_price_buy_in_rub, self.current_price)

    @staticmethod
    def count_percent_profit(start_price: int, now_price: int):  #вынести отсюда нах
        """Считает изменение стоимости с start_price до now_price актива в процентах"""
        try:
            return round((now_price / start_price - 1) * 100, 1)
        except ZeroDivisionError:
            return 0

    @staticmethod
    def get_new_average_price(old_price, new_price, old_size, new_size):
        """Рассчитывает новую среднюю стоимость актива"""
        return round((old_size * old_price + new_size * new_price) / (new_size + old_size), 1)


