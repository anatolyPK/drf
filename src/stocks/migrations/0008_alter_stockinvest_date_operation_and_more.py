# Generated by Django 4.2.5 on 2023-11-18 10:11

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0007_userbond_userbondtransaction_usercurrency_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stockinvest',
            name='date_operation',
            field=models.DateField(default=datetime.datetime(2023, 11, 18, 10, 11, 34, 514978, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='userbondtransaction',
            name='currency',
            field=models.CharField(max_length=12, verbose_name='Валюта покупки'),
        ),
        migrations.AlterField(
            model_name='userbondtransaction',
            name='date_operation',
            field=models.DateField(default=datetime.datetime(2023, 11, 18, 10, 11, 34, 521337, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='usercurrencytransaction',
            name='currency',
            field=models.CharField(max_length=12, verbose_name='Валюта покупки'),
        ),
        migrations.AlterField(
            model_name='usercurrencytransaction',
            name='date_operation',
            field=models.DateField(default=datetime.datetime(2023, 11, 18, 10, 11, 34, 521337, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='useretftransaction',
            name='currency',
            field=models.CharField(max_length=12, verbose_name='Валюта покупки'),
        ),
        migrations.AlterField(
            model_name='useretftransaction',
            name='date_operation',
            field=models.DateField(default=datetime.datetime(2023, 11, 18, 10, 11, 34, 521337, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='usersharetransaction',
            name='currency',
            field=models.CharField(max_length=12, verbose_name='Валюта покупки'),
        ),
        migrations.AlterField(
            model_name='usersharetransaction',
            name='date_operation',
            field=models.DateField(default=datetime.datetime(2023, 11, 18, 10, 11, 34, 521337, tzinfo=datetime.timezone.utc)),
        ),
    ]
