from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class PersonsCrypto(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    token = models.CharField(max_length=16, verbose_name='Токен')
    lot = models.FloatField(verbose_name="Количество")
    average_price_in_rub = models.FloatField(default=0, verbose_name="Средняя цена в рублях")
    average_price_in_usd = models.FloatField(default=0, verbose_name="Средняя цена в $")

    def __str__(self):
        return str(self.user) + '  ' + str(self.token)


class PersonsTransactions(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=3)
    is_buy_or_sell = models.BooleanField(verbose_name='Покупка')
    token_1 = models.CharField(max_length=16, verbose_name="Первый токен")
    token_2 = models.CharField(max_length=16, verbose_name="Второй токен")
    price_in_rub = models.FloatField(default=0, verbose_name="Цена в рублях")
    price_in_usd = models.FloatField(default=0, verbose_name="Цена в $")
    lot = models.FloatField(verbose_name="Количество")
    date_operation = models.DateField(default=timezone.now(), verbose_name="Дата транзакции")

    def __str__(self):
        return self.token_1


class CryptoInvest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='crypto_invest')
    invest_sum_in_rub = models.FloatField()
    invest_sum_in_usd = models.FloatField()
    date_operation = models.DateField(default=timezone.now())

    def __str__(self):
        return str(self.user) + '  ' + str(self.invest_sum_in_rub)


class CryptoPortfolioBalance(models.Model):
    PORTFOLIO_CHOICES = (
        ('crypto', 'crypto'),
        ('stock', 'stock')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='crypto_portfolio_balance')
    portfolio_type = models.CharField(max_length=10, choices=PORTFOLIO_CHOICES, default='crypto')
    sum_in_rub = models.FloatField()
    sum_in_usd = models.FloatField()
    date = models.DateTimeField(default=timezone.now())

    def __str__(self):
        return f'{str(self.user)} {str(self.sum_in_rub)} {str(self.sum_in_usd)} {self.date}'
