from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from deposits.models import PersonsDeposits


class DepositsSchedulers:
    """В методе do_scheduler_jobs добавлены функции, выполняющиеся по заданному расписанию"""
    def __init__(self):
        self.schedulers = BackgroundScheduler()
        self.schedulers.configure(timezone='Asia/Vladivostok')
        self.schedulers.start()

    def do_scheduler_jobs(self):
        schedulers.add_job(self.__add_deposits_capitalization,
                           trigger='cron',
                           hour=00,
                           minute=1)

    def __add_deposits_capitalization(self):
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


schedulers = BackgroundScheduler()
schedulers.configure(timezone='Asia/Vladivostok')
schedulers.start()
a = DepositsSchedulers()
a.do_scheduler_jobs()
