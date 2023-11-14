# Generated by Django 4.2.5 on 2023-11-08 12:10

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crypto', '0012_alter_cryptoinvest_date_operation_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cryptoinvest',
            name='date_operation',
            field=models.DateField(default=datetime.datetime(2023, 11, 8, 12, 10, 38, 297330, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='cryptoportfoliobalance',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2023, 11, 8, 12, 10, 38, 297810, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='personstransactions',
            name='date_operation',
            field=models.DateField(default=datetime.datetime(2023, 11, 8, 12, 10, 38, 296772, tzinfo=datetime.timezone.utc), verbose_name='Дата транзакции'),
        ),
    ]
