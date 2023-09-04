from django.contrib.auth.models import User
from django.db import models


class PersonsCrypto(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=3)
    token = models.CharField(max_length=16)
    lot = models.FloatField()
    average_price = models.FloatField()

    def __str__(self):
        return str(self.user) + '  ' + str(self.token)


class PersonsTransactions(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=3)
    is_buy_or_sell = models.BooleanField()
    token_1 = models.CharField(max_length=16)
    token_2 = models.CharField(max_length=16)
    price = models.FloatField()
    lot = models.FloatField()
    date_operation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token_1

