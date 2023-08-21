class PersonsPortfolio:
    def __init__(self):
        self.total_balance = 0
        self.buy_price = 0
        self.tickers = {}

    def add_active_in_persons_portfolio(self, ident: str, lot: float, average_price_buy: float, current_price: float):
        """Добавление актива в портфель"""
        self.total_balance += current_price * lot
        self.buy_price += average_price_buy * lot
        self.tickers[ident] = AssetsInfo(ident, lot, average_price_buy, current_price)

    def get_portfolio_profit(self):
        return count_percent_profit(self.buy_price, self.total_balance)

    def check_and_returns_params(self, is_get_total_balance,  is_get_profit_in_currency,
                                 is_get_profit_in_percents, is_get_assets):
        """Принимает параметры портфеля, которые нужно отправить клиенту"""
        params_dict = {}
        if is_get_total_balance:
            params_dict['total_balance'] = self.total_balance
        if is_get_profit_in_percents:
            params_dict['profit_in_percents'] = count_percent_profit(self.buy_price, self.total_balance)
        if is_get_profit_in_currency:
            params_dict['profit_in_currency'] = self.total_balance - self.buy_price
        if is_get_assets:
            params_dict['assets'] = {ticker: (self.tickers[ticker].lot, self.tickers[ticker].average_price_buy,
                                              self.tickers[ticker].current_price) for ticker in self.tickers}
        return params_dict


class AssetsInfo:
    """Класс для получения данных о конкретном активе"""
    def __init__(self, ident: str, lot, average_price_buy, current_price):
        self.ident = ident
        self.lot = lot
        self.average_price_buy = average_price_buy
        self.current_price = current_price
        self.total_now_balance = self.current_price * self.lot

    def get_average_cost(self):
        return round(self.total_now_balance / self.lot, 1)

    def count_percent_from_average_to_current_price(self):
        return count_percent_profit(self.average_price_buy, self.current_price)


def count_percent_profit(num_1: int, num_2: int):
    """Считает изменение стоимости с num_1 до num_2 актива в процентах"""
    return round((num_2 / num_1 - 1) * 100, 1)


def get_new_average_price(old_price, new_price, old_size, new_size):
    """Рассчитывает новую среднюю стоимость актива"""
    return round((old_size * old_price + new_size * new_price) / (new_size + old_size), 1)



