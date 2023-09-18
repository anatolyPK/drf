# Generated by Django 4.2.5 on 2023-09-18 00:41

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0013_alter_bond_figi_alter_currency_figi_alter_etf_figi_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bond',
            name='ticker',
            field=models.CharField(max_length=16),
        ),
        migrations.AlterField(
            model_name='currency',
            name='ticker',
            field=models.CharField(max_length=16),
        ),
        migrations.AlterField(
            model_name='etf',
            name='ticker',
            field=models.CharField(max_length=16),
        ),
        migrations.AlterField(
            model_name='share',
            name='ticker',
            field=models.CharField(max_length=16),
        ),
        migrations.AlterField(
            model_name='usertransaction',
            name='date_operation',
            field=models.DateField(default=datetime.datetime(2023, 9, 18, 10, 41, 13, 649704)),
        ),
    ]
