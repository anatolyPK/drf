from deposits.models import PersonsDeposits
from datetime import datetime


def add_or_take_sum_from_deposit(transaction):
    deposit = PersonsDeposits.objects.filter(id=transaction.deposit_id).first()
    deposit.deposits_summ += transaction.size if transaction.is_add_or_take else -transaction.size
    deposit.save()


class DepositsSchedulers:
    def add_deposits_capitalization(self):
        """Проверяет все вклады на капитализацию. Если нужно капитализировать - добавляет к вкладу
        нужную сумму"""
        self.__get_day_now()
        self.__get_all_open_deposits()
        for deposit in self.deposits:
            period_capitalization_in_year, quantity_capitalization_in_year = \
                self.__get_period_and_quantity_of_capitalization(deposit)
            self.__make_capitalization(deposit, period_capitalization_in_year, quantity_capitalization_in_year)

    @staticmethod
    def __get_period_and_quantity_of_capitalization(deposit):
        type_of_capitalization = deposit.percent_capitalization

        if type_of_capitalization == 'daily':
            period_capitalization_in_year, quantity_capitalization_in_year = 1, 365
        elif type_of_capitalization == 'monthly':
            period_capitalization_in_year, quantity_capitalization_in_year = 30, 12
        elif type_of_capitalization == 'annually':
            period_capitalization_in_year, quantity_capitalization_in_year = 365, 1
        else:
            raise Exception('Invalid type of capitalization')

        return period_capitalization_in_year, quantity_capitalization_in_year

    def __make_capitalization(self, deposit, period_capitalization_in_year, quantity_capitalization_in_year):
        if self.__check_dates_for_capitalization(deposit, period_capitalization_in_year):
            self.__add_capitalization(deposit, quantity_capitalization_in_year)

    @staticmethod
    def __add_capitalization(deposit, capitalization_days):
        deposit.deposits_summ += deposit.deposits_summ * deposit.percent / 100 / capitalization_days
        deposit.date_change = datetime.now()
        deposit.save()

    def __get_all_open_deposits(self):
        self.deposits = PersonsDeposits.objects.filter(is_open=True)

    def __check_dates_for_capitalization(self, deposit, capitalization_days):
        date_open = self.__format_deposits_date(deposit)
        if (self.date_now - date_open).days % capitalization_days == 0:
            return True
        return False

    def __get_day_now(self):
        self.date_now = datetime.today().date()

    @staticmethod
    def __format_deposits_date(deposit):
        return deposit.date_open.date()