from .binanceAPI import BinanceAPI
from .models import PersonsCrypto


class PersonsPortfolio:
    IS_GET_TOTAL_BALANCE = True
    IS_GET_PROFIT_IN_CURRENCY = True
    IS_GET_PROFIT_IN_PERCENTS = True
    IS_GET_ASSETS = True

    IS_GET_ASSETS_LOT = True
    IS_GET_ASSETS_AVERAGE_PRICE_BUY = True
    IS_GET_ASSETS_CURRENT_PRICE = True

    def __init__(self, *, type_of_assets: str, person_id: int):
        """Принимает тип актива, с которыми класс будет работать.
        Крипта - 'crypto'
        Фондовый рынок - 'stock'"""
        self.__total_balance = 0
        self.__buy_price = 0
        self.__tickers = {}
        self.__type_of_assets = type_of_assets
        self.__person_id = person_id
        self.__make_portfolio()

    def __make_portfolio(self):
        personal_assets = self.__get_datas_from_model()
        idents = [asset.token + 'usdt' for asset in personal_assets]
        current_prices_of_assets = BinanceAPI.get_tickers_prices(idents)
        for asset in personal_assets:
            self.__add_active_in_persons_portfolio(ident=asset.token,
                                                   lot=asset.size,
                                                   average_price_buy=asset.average_price,
                                                   current_price=current_prices_of_assets[asset.token.upper() + 'USDT'])

    def __add_active_in_persons_portfolio(self, ident: str, lot: float, average_price_buy: float, current_price: float):
        """Добавление актива в портфель"""
        self.__total_balance += current_price * lot
        self.__buy_price += average_price_buy * lot
        self.__tickers[ident] = AssetsInfo(ident, lot, average_price_buy, current_price)

    def __get_portfolio_profit_from_average_to_current_price(self):
        return AssetsInfo.count_percent_profit(self.__buy_price, self.__total_balance)

    def returns_info_about_portfolio_and_assets(self):
        """Принимает параметры портфеля, которые нужно отправить клиенту"""
        params_dict = {}
        if self.IS_GET_TOTAL_BALANCE:
            params_dict['total_balance'] = self.__total_balance
        if self.IS_GET_PROFIT_IN_PERCENTS:
            params_dict['profit_in_percents'] = AssetsInfo.count_percent_profit(self.__buy_price, self.__total_balance)
        if self.IS_GET_PROFIT_IN_CURRENCY:
            params_dict['profit_in_currency'] = self.__total_balance - self.__buy_price
        if self.IS_GET_ASSETS:
            params_dict['assets'] = self.__get_info_about_assets()
        return params_dict

    def __get_info_about_assets(self):
        tickers_info = {}
        for ticker in self.__tickers:
            tickers_info[ticker] = []
            if self.IS_GET_ASSETS_LOT:
                tickers_info[ticker].append(self.__tickers[ticker].lot)
            if self.IS_GET_ASSETS_AVERAGE_PRICE_BUY:
                tickers_info[ticker].append(self.__tickers[ticker].average_price_buy)
            if self.IS_GET_ASSETS_CURRENT_PRICE:
                tickers_info[ticker].append(self.__tickers[ticker].current_price)
        return tickers_info

    def __get_datas_from_model(self):
        if self.__type_of_assets == 'crypto':
            return PersonsCrypto.objects.all().filter(person_id=self.__person_id)


class AssetsInfo:
    """Класс для получения данных и вычисления значений конкретного актива"""
    def __init__(self, ident: str, lot, average_price_buy, current_price):
        self.ident = ident
        self.lot = lot
        self.average_price_buy = average_price_buy
        self.current_price = current_price
        self.total_now_balance = self.current_price * self.lot

    def __get_average_cost(self):
        return round(self.total_now_balance / self.lot, 1)

    def __count_percent_from_average_to_current_price(self):
        return self.count_percent_profit(self.average_price_buy, self.current_price)

    @staticmethod
    def count_percent_profit(num_1: int, num_2: int):
        """Считает изменение стоимости с num_1 до num_2 актива в процентах"""
        try:
            return round((num_2 / num_1 - 1) * 100, 1)
        except ZeroDivisionError:
            return 0

    @staticmethod
    def get_new_average_price(old_price, new_price, old_size, new_size):
        """Рассчитывает новую среднюю стоимость актива"""
        return round((old_size * old_price + new_size * new_price) / (new_size + old_size), 1)




