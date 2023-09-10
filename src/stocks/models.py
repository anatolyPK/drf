from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models


class UserStock(models.Model):
    """Модель, хранящая данные об активах пользователей"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    figi = models.CharField(max_length=32, verbose_name='figi инструмента')
    lot = models.FloatField(verbose_name='Количество актива')
    average_price_in_rub = models.FloatField(verbose_name='Средняя цена в рублях', default=0)
    average_price_in_usd = models.FloatField(verbose_name='Средняя цена в долларах', default=0)

    def __str__(self):
        return str(self.user) + '  ' + str(self.figi)


class UserTransaction(models.Model):
    """Модель, хранящая данные о транзакциях активов пользователей"""

    CHOICES_OPERATION_TYPE = [
        (1, 'Покупка'),
        (0, 'Продажа'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_buy_or_sell = models.BooleanField(verbose_name='Операция', choices=CHOICES_OPERATION_TYPE)
    figi = models.CharField(max_length=16, verbose_name='figi инструмента')
    currency = models.CharField(max_length=16, verbose_name='Валюта покупки')
    price_in_rub = models.FloatField(verbose_name='Цена на момент покупки в рублях', default=0)
    price_in_usd = models.FloatField(verbose_name='Цена на момент покупки в долларах', default=0)
    lot = models.FloatField(verbose_name='Количество актива')
    date_operation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.figi


class AssetsList:
    figi = models.CharField(max_length=16)
    name = models.CharField(max_length=128)


class CommonAssetsInfo(models.Model):
    figi = models.CharField(max_length=16)
    ticker = models.CharField(max_length=10)
    name = models.CharField(max_length=128)
    currency = models.CharField( max_length=10, verbose_name='Валюта актива')
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

