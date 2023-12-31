from datetime import datetime

from django.contrib.auth.models import User
from django.db import models


class PersonsCrypto(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=3)
    token = models.CharField(max_length=16)
    lot = models.FloatField()
    average_price_in_rub = models.FloatField(default=0)
    average_price_in_usd = models.FloatField(default=0)

    def __str__(self):
        return str(self.user) + '  ' + str(self.token)


class PersonsTransactions(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=3)
    is_buy_or_sell = models.BooleanField()
    token_1 = models.CharField(max_length=16)
    token_2 = models.CharField(max_length=16)
    price_in_rub = models.FloatField(default=0)
    price_in_usd = models.FloatField(default=0)
    lot = models.FloatField()
    date_operation = models.DateField(default=datetime.now())

    def __str__(self):
        return self.token_1

