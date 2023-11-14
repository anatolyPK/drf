from datetime import datetime, date, timedelta

from django.utils import timezone

from stocks.models import Bond, Coupon
from stocks.services.tinkoff_API import TinkoffAPI, convert_tinkoff_money_in_currency

import logging


logger_debug = logging.getLogger('debug')


class BondCalculatorService:
    def __init__(self, bond, is_tax):
        self.TAX = 0.87 if is_tax else 1.0
        self.ROUND_DGT = 2

        self.figi = bond.figi
        self.name = bond.name
        self.nominal = bond.nominal
        self.placement_date = bond.placement_date
        self.maturity_date = bond.maturity_date
        self.coupon_quantity_per_year = bond.coupon_quantity_per_year

        self.aci_value = TinkoffAPI.get_aci(figi=bond.figi)
        self.market_price = TinkoffAPI.get_last_price_asset(figi=[bond.figi])[bond.figi]
        self._coupons = TinkoffAPI.get_coupons(figi=self.figi)  # мб не нужен здесь
        self.yearly_payment = self._get_yearly_payment()
        self.total_coupons_quantity = len(self._coupons)
        self.coupons_to_maturity = self._get_coupons_to_maturity()
        self.years_to_maturity = self._get_years_to_maturity()

    def _get_coupons_to_maturity(self):
        date_today = datetime.combine(date.today(), datetime.min.time())
        if timezone.is_aware(date_today):
            date_today = timezone.make_naive(date_today)

        coupons = []
        for coupon in self._coupons:
            coupon_date = coupon.coupon_date
            if timezone.is_aware(coupon_date):
                coupon_date = timezone.make_naive(coupon_date)
            if date_today < coupon_date:
                coupons.append(coupon)

        logger_debug.debug(f' {len(coupons)}')

        return coupons

    def _get_yearly_payment(self):#сделать, чтобы считал текущий год, а не следующий
        year = self.placement_date.year + 1

        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)

        total_payment = 0
        payment_per_year = 0

        if timezone.is_aware(start_date):
            start_date = timezone.make_naive(start_date)
        if timezone.is_aware(end_date):
            end_date = timezone.make_naive(end_date)

        for coupon in self._coupons:
            coupon_date_naive = timezone.make_naive(coupon.coupon_date)
            if start_date <= coupon_date_naive <= end_date:
                total_payment += convert_tinkoff_money_in_currency(coupon.pay_one_bond)
                payment_per_year += 1
            if payment_per_year == self.coupon_quantity_per_year:
                break

        if payment_per_year != self.coupon_quantity_per_year:
            logger_debug.debug(f'{payment_per_year} != {self.coupon_quantity_per_year}')
        logger_debug.debug(f'PAYMENT PER YEAR: {total_payment}')
        return total_payment * self.TAX

    def _get_years_to_maturity(self):
        delta = abs(self.maturity_date - date.today())
        logger_debug.debug(f'YEARS: {delta.days / 365}')
        return round(delta.days / 365, self.ROUND_DGT)


class BondCalculator(BondCalculatorService):
    def __init__(self, bond: Bond, is_tax: bool):
        super().__init__(bond, is_tax)
        self.nominal_yield = self._get_nominal_yield_to_maturity()
        self.current_yield = self._get_current_yield()
        self.adjusted_current_yield = self._get_adjusted_current_yield()
        self.effective_yield = self._get_effective_yield()
        self.ytm = self._get_ytm()

    def _get_nominal_yield_to_maturity(self):
        logger_debug.debug(f'Nominal yield: {self.yearly_payment / self.nominal * 100}')
        return round(self.yearly_payment / self.nominal * 100, self.ROUND_DGT)

    def _get_current_yield(self):
        """Рассчитывает текущую доходность с УЧЕТОМ НКД"""
        logger_debug.debug(f'MARKET PRICE: {self.market_price * 10}')
        logger_debug.debug(f'Current Yield: {self.yearly_payment / (self.market_price * 10 + self.aci_value) * 100}')
        return round(self.yearly_payment / (self.market_price * 10 + self.aci_value) * 100, self.ROUND_DGT)

    def _get_adjusted_current_yield(self):
        """Рассчитывает скорректированную доходность с УЧЕТОМ НКД и цены погашения"""
        logger_debug.debug(f'ADJUSTED CURRENT: {self.current_yield + (100 - self.market_price - self.aci_value / 100) / self.years_to_maturity}')
        return round(self.current_yield + (100 - self.market_price - self.aci_value / 100) / self.years_to_maturity, self.ROUND_DGT)

    def _get_effective_yield(self):
        top = ((self.nominal - self.market_price * 10 - self.aci_value) / self.years_to_maturity
               + self.yearly_payment)
        bot = (0.4 * self.nominal + 0.6 * self.market_price * 10)
        logger_debug.debug(f'EFFECTIVE: {top * 100 / bot}')
        return round(top * 100 / bot, self.ROUND_DGT)

    def _get_ytm(self, step=0.000015, max_iterations=10000, tolerance=0.15):
        left = self.market_price * 10 + self.aci_value
        ytm_value = self.current_yield / 100
        date_today = datetime.combine(date.today(), datetime.min.time())

        for _ in range(max_iterations):
            right_sum = 0
            for i in range(len(self.coupons_to_maturity)):
                pay_one_bond = convert_tinkoff_money_in_currency(self.coupons_to_maturity[i].pay_one_bond) * self.TAX
                if i == len(self.coupons_to_maturity) - 1:
                    pay_one_bond += self.nominal

                coupon_date = timezone.make_naive(self.coupons_to_maturity[i].coupon_date)

                right_sum += pay_one_bond / (1 + ytm_value) ** ((coupon_date - date_today).days / 365)
            if abs(left - right_sum) < tolerance:
                return ytm_value * 100
            ytm_value += step
        return ytm_value
