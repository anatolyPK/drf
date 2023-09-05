from django.contrib.auth.models import User
from django.db import models


class UserStock(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    figi = models.CharField(max_length=32)
    lot = models.FloatField()
    average_price = models.FloatField()

    def __str__(self):
        return str(self.user) + '  ' + str(self.figi)


class UserTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_buy_or_sell = models.BooleanField()
    figi = models.CharField(max_length=16)
    currency = models.CharField(max_length=16)
    price = models.FloatField()
    lot = models.FloatField()
    date_operation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.figi


class CommonAssetsInfo(models.Model):
    figi = models.CharField(max_length=16)
    ticker = models.CharField(max_length=10)
    name = models.CharField(max_length=128)
    currency = models.CharField(max_length=10, verbose_name='Валюта актива')
    buy_available_flag = models.BooleanField(verbose_name='Доступна ли для покупки')
    sell_available_flag = models.BooleanField(verbose_name='Доступна ли для продажи')
    for_iis_flag = models.BooleanField(verbose_name='Доступна ли для ИИС')
    for_qual_investor_flag = models.BooleanField(verbose_name='Доступна ли только для квал инвесторов')
    exchange = models.CharField(max_length=50, verbose_name='Биржа')

    class Meta:
        abstract = True


class Share(CommonAssetsInfo):
    lot = models.FloatField()
    nominal = models.FloatField()
    country_of_risk = models.CharField(max_length=4, verbose_name='Страна акции')
    sector = models.CharField(max_length=32)
    div_yield_flag = models.BooleanField(verbose_name='Платит ли дивиденды')
    share_type = models.CharField(max_length=10, verbose_name='Тип акции по классификации Тинькоф')


class Bond(CommonAssetsInfo):
    nominal = models.FloatField(verbose_name='Номинал облигации')
    initial_nominal = models.FloatField(verbose_name='Изначальный номинал облигации')
    aci_value = models.FloatField(verbose_name='Значение НКД (накопленного купонного дохода) на дату')
    country_of_risk = models.CharField(max_length=4, verbose_name='Страна облигации')
    sector = models.CharField(max_length=32)
    floating_coupon_flag = models.BooleanField(verbose_name='Переменный ли купон')
    perpetual_flag = models.BooleanField(verbose_name='Признак бессрочной облигации')
    amortization_flag = models.BooleanField(verbose_name='Признак облигации с амортизацией долга')
    risk_level = models.CharField(max_length=10, verbose_name='Уровень риска')


class Etf(CommonAssetsInfo):
    fixed_commission = models.FloatField(verbose_name='Комиссия фонда')
    focus_type = models.CharField(max_length=50, verbose_name='Активы фонда')
    country_of_risk = models.CharField(max_length=4, verbose_name='Страна облигации')
    sector = models.CharField(max_length=32)


class Currency(CommonAssetsInfo):
    lot = models.FloatField()
    nominal = models.FloatField()
    country_of_risk = models.CharField(max_length=4, verbose_name='Страна валюты')
    min_price_increment = models.FloatField()

