import time

from .tinkoff_API import TinkoffAPI, convert_tinkoff_money_in_currency
from ..models import Share, Bond, Etf, Currency, Coupon
from datetime import datetime

import logging


logger = logging.getLogger('debug')


class TinkoffAssetsDB:
    @classmethod
    def write_db_actual_shares(cls, actual_shares):
        new_shares = []
        for share in actual_shares.instruments:
            if cls.__check_assets_in_bd(share, Share):
                new_share = Share(
                    figi=share.figi,
                    ticker=share.ticker,
                    name=share.name,
                    currency=share.currency,
                    buy_available_flag=share.buy_available_flag,
                    sell_available_flag=share.sell_available_flag,
                    for_iis_flag=share.for_iis_flag,
                    for_qual_investor_flag=share.for_qual_investor_flag,
                    exchange=share.exchange,
                    lot=share.lot,
                    nominal=convert_tinkoff_money_in_currency(share.nominal),
                    country_of_risk=share.country_of_risk,
                    sector=share.sector,
                    div_yield_flag=share.div_yield_flag,
                    share_type=share.share_type
                )
                new_shares.append(new_share)
        Share.objects.bulk_create(new_shares)

    @classmethod
    def write_db_actual_bonds(cls, actual_bonds):
        new_bonds = []
        for bond in actual_bonds.instruments:
            if cls.__check_assets_in_bd(bond, Bond):
                new_bond = Bond(
                    figi=bond.figi,
                    ticker=bond.ticker,
                    name=bond.name,
                    currency=bond.currency,
                    buy_available_flag=bond.buy_available_flag,
                    sell_available_flag=bond.sell_available_flag,
                    for_iis_flag=bond.for_iis_flag,
                    for_qual_investor_flag=bond.for_qual_investor_flag,
                    exchange=bond.exchange,
                    nominal=convert_tinkoff_money_in_currency(bond.nominal),
                    initial_nominal=convert_tinkoff_money_in_currency(bond.initial_nominal),
                    aci_value=convert_tinkoff_money_in_currency(bond.aci_value),
                    country_of_risk=bond.country_of_risk,
                    sector=bond.sector,
                    floating_coupon_flag=bond.floating_coupon_flag,
                    perpetual_flag=bond.perpetual_flag,
                    amortization_flag=bond.amortization_flag,
                    risk_level=bond.risk_level,
                    maturity_date=bond.maturity_date,
                    placement_date=bond.placement_date,
                    coupon_quantity_per_year=bond.coupon_quantity_per_year,
                )
                new_bonds.append(new_bond)
        Bond.objects.bulk_create(new_bonds)

    @classmethod
    def write_db_actual_etfs(cls, actual_etfs):
        new_etfs = []
        for etf in actual_etfs.instruments:
            if cls.__check_assets_in_bd(etf, Etf):
                new_etf = Etf(
                    figi=etf.figi,
                    ticker=etf.ticker,
                    name=etf.name,
                    currency=etf.currency,
                    buy_available_flag=etf.buy_available_flag,
                    sell_available_flag=etf.sell_available_flag,
                    for_iis_flag=etf.for_iis_flag,
                    for_qual_investor_flag=etf.for_qual_investor_flag,
                    exchange=etf.exchange,
                    fixed_commission=convert_tinkoff_money_in_currency(etf.fixed_commission),
                    focus_type=etf.focus_type,
                    country_of_risk=etf.country_of_risk,
                    sector=etf.sector
                )
                new_etfs.append(new_etf)
        Etf.objects.bulk_create(new_etfs)

    @classmethod
    def write_db_actual_currencies(cls, actual_currencies):
        new_currencies = []
        for currency in actual_currencies.instruments:
            if cls.__check_assets_in_bd(currency, Currency):
                new_etf = Currency(
                    figi=currency.figi,
                    ticker=currency.ticker,
                    name=currency.name,
                    currency=currency.currency,
                    buy_available_flag=currency.buy_available_flag,
                    sell_available_flag=currency.sell_available_flag,
                    for_iis_flag=currency.for_iis_flag,
                    for_qual_investor_flag=currency.for_qual_investor_flag,
                    exchange=currency.exchange,
                    lot=currency.lot,
                    nominal=convert_tinkoff_money_in_currency(currency.nominal),
                    country_of_risk=currency.country_of_risk,
                    min_price_increment=convert_tinkoff_money_in_currency(currency.min_price_increment)
                )
                new_currencies.append(new_etf)
        Currency.objects.bulk_create(new_currencies)

    @classmethod
    def write_db_actual_coupons(cls):
        bonds = Bond.objects.all()
        new_coupons = []
        for bond in bonds:
            if not bond.coupons.exists():
                try:
                    coupons = TinkoffAPI.get_coupons(figi=bond.figi)

                    for coupon in coupons:
                        new_coupon = Coupon(
                            figi=bond,
                            coupon_date=coupon.coupon_date,
                            coupon_number=coupon.coupon_number,
                            pay_one_bond=convert_tinkoff_money_in_currency(coupon.pay_one_bond),
                            coupon_start_date=coupon.coupon_start_date,
                            coupon_end_date=coupon.coupon_end_date,
                            coupon_period=coupon.coupon_period,
                            coupon_type=coupon.coupon_type,
                        )
                        new_coupons.append(new_coupon)
                except Exception:
                    pass
                # time.sleep(0.01)
            if len(new_coupons) > 80:
                Coupon.objects.bulk_create(new_coupons)
                new_coupons = []

    @staticmethod
    def __check_assets_in_bd(asset, model):
        if not model.objects.filter(figi=asset.figi):
            return True
        return False


class TinkoffAssets(TinkoffAssetsDB):
    @classmethod
    def update_all_assets(cls):
        """Обновляет список всех акций, облигаций, etf, валют.
        Рекомендуется запускать раз в месяц во время слабого трафика, так как
        скорость выполнения от 2 до 20 сек в среднем."""
        print(f'Start update {datetime.now()}')
        cls.update_all_shares()
        cls.update_all_bonds()
        cls.update_all_etfs()
        cls.update_all_currencies()
        print(f'stop {datetime.now()}')

    @classmethod
    def update_all_shares(cls):
        actual_shares = TinkoffAPI.get_actual_tinkoff_shares()
        cls.write_db_actual_shares(actual_shares)

    @classmethod
    def update_all_bonds(cls):
        actual_bonds = TinkoffAPI.get_actual_tinkoff_bonds()
        cls.write_db_actual_bonds(actual_bonds)

    @classmethod
    def update_all_etfs(cls):
        actual_etfs = TinkoffAPI.get_actual_tinkoff_etfs()
        cls.write_db_actual_etfs(actual_etfs)

    @classmethod
    def update_all_currencies(cls):
        actual_currencies = TinkoffAPI.get_actual_tinkoff_currencies()
        cls.write_db_actual_currencies(actual_currencies)

    @classmethod
    def update_all_coupons(cls):
        cls.write_db_actual_coupons()

