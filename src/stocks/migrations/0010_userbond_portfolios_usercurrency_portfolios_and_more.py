# Generated by Django 4.2.5 on 2023-11-30 01:09

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0009_portfolio_alter_stockinvest_date_operation_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userbond',
            name='portfolios',
            field=models.ManyToManyField(blank=True, default=None, related_name='user_bonds', to='stocks.portfolio'),
        ),
        migrations.AddField(
            model_name='usercurrency',
            name='portfolios',
            field=models.ManyToManyField(blank=True, default=None, related_name='user_currencies', to='stocks.portfolio'),
        ),
        migrations.AddField(
            model_name='useretf',
            name='portfolios',
            field=models.ManyToManyField(blank=True, default=None, related_name='user_etf', to='stocks.portfolio'),
        ),
        migrations.AddField(
            model_name='usershare',
            name='portfolios',
            field=models.ManyToManyField(blank=True, default=None, related_name='user_shares', to='stocks.portfolio'),
        ),
        migrations.AlterField(
            model_name='stockinvest',
            name='date_operation',
            field=models.DateField(default=datetime.datetime(2023, 11, 30, 1, 9, 9, 264028, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='userbondtransaction',
            name='date_operation',
            field=models.DateField(default=datetime.datetime(2023, 11, 30, 1, 9, 9, 278958, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='usercurrencytransaction',
            name='date_operation',
            field=models.DateField(default=datetime.datetime(2023, 11, 30, 1, 9, 9, 278958, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='useretftransaction',
            name='date_operation',
            field=models.DateField(default=datetime.datetime(2023, 11, 30, 1, 9, 9, 278958, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='usersharetransaction',
            name='date_operation',
            field=models.DateField(default=datetime.datetime(2023, 11, 30, 1, 9, 9, 278958, tzinfo=datetime.timezone.utc)),
        ),
        migrations.DeleteModel(
            name='PortfolioAsset',
        ),
    ]
