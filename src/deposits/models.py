from django.contrib.auth.models import User
from django.db import models


class PersonsDeposits(models.Model):
    CHOICES_PERCENT = [
        ('daily', 'daily'),
        ('monthly', 'monthly'),
        ('annually', 'annually')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    deposits_summ = models.FloatField(null=True)
    description = models.CharField(max_length=256)
    is_open = models.BooleanField(default=1)
    date_open = models.DateTimeField(auto_now_add=True)
    percent = models.FloatField()
    percent_capitalization = models.CharField(max_length=12, choices=CHOICES_PERCENT)
    date_change = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user) + '  ' + str(self.description)


class PersonDepositsTransactions(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    deposit_id = models.IntegerField()
    is_add_or_take = models.BooleanField()
    size = models.FloatField()
    date_operation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.size)
