from django.db import models


class PersonsDeposits(models.Model):
    CHOICES_PERCENT = [
        ('daily', 'daily'),
        ('monthly', 'monthly'),
        ('annually', 'annually')
    ]

    person_id = models.IntegerField()
    deposits_summ = models.FloatField(null=True)
    description = models.CharField(max_length=256)
    is_open = models.BooleanField(default=1)
    date_open = models.DateTimeField(auto_now_add=True)
    percent = models.FloatField()
    percent_capitalization = models.CharField(max_length=12, choices=CHOICES_PERCENT)
    date_change = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.person_id) + '  ' + str(self.description)


class PersonDepositsTransactions(models.Model):
    person_id = models.IntegerField()
    deposit_id = models.IntegerField()
    is_add_or_take = models.BooleanField()
    size = models.FloatField()
    date_operation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.size)
