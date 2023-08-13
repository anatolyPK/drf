from django.db import models


class PersonsCrypto(models.Model):
    person_id = models.IntegerField()
    token = models.CharField(max_length=16)
    size = models.FloatField()
    average_price = models.FloatField()

    def __str__(self):
        return str(self.person_id) + '  ' + str(self.token)


class PersonsTransactions(models.Model):
    person_id = models.IntegerField()
    is_buy_or_sell = models.BooleanField()
    token_1 = models.CharField(max_length=16)
    token_2 = models.CharField(max_length=16)
    price = models.FloatField()
    lot = models.FloatField()
    date_operation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token_1

