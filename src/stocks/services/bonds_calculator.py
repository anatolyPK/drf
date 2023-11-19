from datetime import datetime, date, timedelta

from django.utils import timezone

from stocks.models import Bond, Coupon
from stocks.services.tinkoff_API import TinkoffAPI

import logging


logger_debug = logging.getLogger('debug')


ROUND_DIGIT = 2


class BaseBond:
    def __init__(self, bond, tax_size):
        self.figi = bond.figi
        self.name = bond.name
        self.nominal = bond.nominal
        self.currency = bond.currency
        self.currency_nominal = bond.currency_nominal
        self.placement_date = bond.placement_date
        self.maturity_date = bond.maturity_date
        self.coupon_quantity_per_year = bond.coupon_quantity_per_year
        self.tax = PriceAndTax.get_tax(tax_size=tax_size)
        self.market_price = PriceAndTax.get_market_price(figi=bond.figi)
        self.coupon_info = CouponHandling(bond=bond, tax=self.tax)
        self.aci_value = BondCalculatorService.count_aci(coupon_info=self.coupon_info)
        self.years_to_maturity = BondCalculatorService.get_years_to_maturity(self.maturity_date)
        self.market_price_with_aci = PriceAndTax.get_market_price_with_aci(market_price=self.market_price,
                                                                           aci=self.aci_value)

        self.rounded_market_price = round(self.market_price, ROUND_DIGIT)
        self.rounded_aci_value = round(self.aci_value, ROUND_DIGIT)
        self.rounded_years_to_maturity = round(self.years_to_maturity, ROUND_DIGIT)
        self.rounded_market_price_with_aci = round(self.market_price_with_aci, ROUND_DIGIT)


class PriceAndTax:
    @staticmethod
    def get_market_price(figi):
        return TinkoffAPI.get_last_price_asset(figi=[figi])[figi]

    @staticmethod
    def get_market_price_with_aci(market_price, aci):
        return market_price + aci / 10

    @staticmethod
    def get_tax(tax_size):
        logger_debug.debug(f'{tax_size} {type(tax_size)}')
        if tax_size == '0':
            return 1
        elif tax_size == '13':
            return 0.87
        elif tax_size == '15':
            return 0.85
        else:
            logger_debug.debug(f'Неверно передан tax_size: {tax_size}')


class CouponCalculations:
    @staticmethod
    def count_days_to_next_coupon(next_coupon):
        logger_debug.debug(f'Days to coupon {(timezone.make_naive(next_coupon.coupon_date) - datetime.now()).days}')
        return (timezone.make_naive(next_coupon.coupon_date) - datetime.now()).days

    @staticmethod
    def get_coupons_to_maturity(all_coupons, coupon_quantity_per_year):
        next_coupon, prev_coupon = None, None
        date_today = datetime.combine(date.today(), datetime.min.time())
        if timezone.is_aware(date_today):
            date_today = timezone.make_naive(date_today)

        coupons = []
        for coupon in all_coupons:
            coupon_date = coupon.coupon_date
            if timezone.is_aware(coupon_date):
                coupon_date = timezone.make_naive(coupon_date)
            if date_today < coupon_date:
                coupons.append(coupon)

            if abs((date_today - coupon_date).days) < 365 / coupon_quantity_per_year:
                if (date_today - coupon_date).days < 0:
                    next_coupon = coupon
                else:
                    prev_coupon = coupon
        return coupons, next_coupon, prev_coupon

    @staticmethod
    def get_yearly_payment(bond, coupons, tax):#сделать, чтобы считал текущий год, а не следующий
        year = bond.placement_date.year + 1

        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)

        total_payment = 0
        payment_per_year = 0

        if timezone.is_aware(start_date):
            start_date = timezone.make_naive(start_date)
        if timezone.is_aware(end_date):
            end_date = timezone.make_naive(end_date)

        for coupon in coupons:
            coupon_date_naive = timezone.make_naive(coupon.coupon_date)
            if start_date <= coupon_date_naive <= end_date:
                total_payment += coupon.pay_one_bond
                payment_per_year += 1
            if payment_per_year == bond.coupon_quantity_per_year:
                break

        if payment_per_year != bond.coupon_quantity_per_year:
            logger_debug.debug(f'{payment_per_year} != {bond.coupon_quantity_per_year}')
        logger_debug.debug(f'PAYMENT PER YEAR: {total_payment}')
        return total_payment * tax


class CouponHandling:
    def __init__(self, bond, tax):
        self.bond_coupons = self.get_coupons_from_db(bond=bond)
        self.coupons_to_maturity, self.next_coupon, self.prev_coupon = (
            CouponCalculations.get_coupons_to_maturity(all_coupons=self.bond_coupons,
                                                       coupon_quantity_per_year=bond.coupon_quantity_per_year))
        self.days_to_next_coupon = CouponCalculations.count_days_to_next_coupon(next_coupon=self.next_coupon)
        self.coupons_quantity = len(self.bond_coupons)
        self.yearly_coupon_payment = CouponCalculations.get_yearly_payment(bond=bond, coupons=self.bond_coupons,
                                                                           tax=tax)
        self.next_coupon_size = self.next_coupon.pay_one_bond

    @staticmethod
    def get_coupons_from_db(bond):
        return Coupon.objects.filter(figi=bond)


class BondCalculatorService:

    @staticmethod
    def count_aci(coupon_info):
        next_coupon_date = timezone.make_naive(coupon_info.next_coupon.coupon_date)
        date_start_coupon_period = timezone.make_naive(coupon_info.next_coupon.coupon_start_date)
        aci = (coupon_info.next_coupon.pay_one_bond *
               ((next_coupon_date - date_start_coupon_period).days - coupon_info.days_to_next_coupon) /
               (next_coupon_date - date_start_coupon_period).days)
        return aci

    @staticmethod
    def get_years_to_maturity(maturity_date):
        delta = abs(maturity_date - date.today())
        logger_debug.debug(f'YEARS: {delta.days / 365}')
        return delta.days / 365


class BondCalculator(BaseBond):
    def __init__(self, bond: Bond, tax_size: int):
        super().__init__(bond, tax_size)
        self.nominal_yield = self._get_nominal_yield_to_maturity()
        self.current_yield = self._get_current_yield()
        self.adjusted_current_yield = self._get_adjusted_current_yield()
        self.ytm = self._get_ytm()

        self.rounded_nominal_yield = round(self.nominal_yield, ROUND_DIGIT)
        self.rounded_current_yield = round(self.current_yield, ROUND_DIGIT)
        self.rounded_adjusted_current_yield = round(self.adjusted_current_yield, ROUND_DIGIT)
        self.rounded_ytm = round(self.ytm, ROUND_DIGIT)

    def _get_nominal_yield_to_maturity(self):
        logger_debug.debug(f'Nominal yield: {self.coupon_info.yearly_coupon_payment / self.nominal * 100}')
        return self.coupon_info.yearly_coupon_payment / self.nominal * 100

    def _get_current_yield(self):
        """Рассчитывает текущую доходность с УЧЕТОМ НКД"""
        logger_debug.debug(f'MARKET PRICE: {self.market_price * 10}')
        logger_debug.debug(f'Current Yield: {self.coupon_info.yearly_coupon_payment / (self.market_price * 10 + self.aci_value) * 100}')
        return self.coupon_info.yearly_coupon_payment / (self.market_price * 10 + self.aci_value) * 100

    def _get_adjusted_current_yield(self):
        """Рассчитывает скорректированную доходность с УЧЕТОМ НКД и цены погашения"""
        logger_debug.debug(f'ADJUSTED CURRENT: {self.current_yield + (100 - self.market_price - self.aci_value / 100) / self.years_to_maturity}')
        return self.current_yield + (100 - self.market_price - self.aci_value / 100) / self.years_to_maturity

    def _get_ytm(self, step=0.000015, max_iterations=10000, tolerance=0.15):
        left = self.market_price * 10 + self.aci_value
        ytm_value = self.current_yield / 100
        date_today = datetime.combine(date.today(), datetime.min.time())

        for _ in range(max_iterations):
            right_sum = 0
            for i in range(len(self.coupon_info.coupons_to_maturity)):
                pay_one_bond = self.coupon_info.coupons_to_maturity[i].pay_one_bond * self.tax
                if i == len(self.coupon_info.coupons_to_maturity) - 1:
                    pay_one_bond += self.nominal

                coupon_date = timezone.make_naive(self.coupon_info.coupons_to_maturity[i].coupon_date)

                right_sum += pay_one_bond / (1 + ytm_value) ** ((coupon_date - date_today).days / 365)
            if abs(left - right_sum) < tolerance:
                return ytm_value * 100
            ytm_value += step
        return ytm_value
