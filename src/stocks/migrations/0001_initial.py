# Generated by Django 4.2.5 on 2023-09-17 06:22

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bond',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('figi', models.CharField(max_length=16)),
                ('ticker', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=128)),
                ('currency', models.CharField(max_length=10, verbose_name='Валюта актива')),
                ('buy_available_flag', models.BooleanField(verbose_name='Доступна ли для покупки')),
                ('sell_available_flag', models.BooleanField(verbose_name='Доступна ли для продажи')),
                ('for_iis_flag', models.BooleanField(verbose_name='Доступна ли для ИИС')),
                ('for_qual_investor_flag', models.BooleanField(verbose_name='Доступна ли только для квал инвесторов')),
                ('exchange', models.CharField(max_length=50, verbose_name='Биржа')),
                ('nominal', models.FloatField(verbose_name='Номинал облигации')),
                ('initial_nominal', models.FloatField(verbose_name='Изначальный номинал облигации')),
                ('aci_value', models.FloatField(verbose_name='Значение НКД (накопленного купонного дохода) на дату')),
                ('country_of_risk', models.CharField(max_length=4, verbose_name='Страна облигации')),
                ('sector', models.CharField(max_length=32)),
                ('floating_coupon_flag', models.BooleanField(verbose_name='Переменный ли купон')),
                ('perpetual_flag', models.BooleanField(verbose_name='Признак бессрочной облигации')),
                ('amortization_flag', models.BooleanField(verbose_name='Признак облигации с амортизацией долга')),
                ('risk_level', models.CharField(max_length=10, verbose_name='Уровень риска')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('figi', models.CharField(max_length=16)),
                ('ticker', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=128)),
                ('currency', models.CharField(max_length=10, verbose_name='Валюта актива')),
                ('buy_available_flag', models.BooleanField(verbose_name='Доступна ли для покупки')),
                ('sell_available_flag', models.BooleanField(verbose_name='Доступна ли для продажи')),
                ('for_iis_flag', models.BooleanField(verbose_name='Доступна ли для ИИС')),
                ('for_qual_investor_flag', models.BooleanField(verbose_name='Доступна ли только для квал инвесторов')),
                ('exchange', models.CharField(max_length=50, verbose_name='Биржа')),
                ('lot', models.FloatField()),
                ('nominal', models.FloatField()),
                ('country_of_risk', models.CharField(max_length=4, verbose_name='Страна валюты')),
                ('min_price_increment', models.FloatField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Etf',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('figi', models.CharField(max_length=16)),
                ('ticker', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=128)),
                ('currency', models.CharField(max_length=10, verbose_name='Валюта актива')),
                ('buy_available_flag', models.BooleanField(verbose_name='Доступна ли для покупки')),
                ('sell_available_flag', models.BooleanField(verbose_name='Доступна ли для продажи')),
                ('for_iis_flag', models.BooleanField(verbose_name='Доступна ли для ИИС')),
                ('for_qual_investor_flag', models.BooleanField(verbose_name='Доступна ли только для квал инвесторов')),
                ('exchange', models.CharField(max_length=50, verbose_name='Биржа')),
                ('fixed_commission', models.FloatField(verbose_name='Комиссия фонда')),
                ('focus_type', models.CharField(max_length=50, verbose_name='Активы фонда')),
                ('country_of_risk', models.CharField(max_length=4, verbose_name='Страна облигации')),
                ('sector', models.CharField(max_length=32)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Share',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('figi', models.CharField(max_length=16)),
                ('ticker', models.CharField(max_length=10)),
                ('name', models.CharField(max_length=128)),
                ('currency', models.CharField(max_length=10, verbose_name='Валюта актива')),
                ('buy_available_flag', models.BooleanField(verbose_name='Доступна ли для покупки')),
                ('sell_available_flag', models.BooleanField(verbose_name='Доступна ли для продажи')),
                ('for_iis_flag', models.BooleanField(verbose_name='Доступна ли для ИИС')),
                ('for_qual_investor_flag', models.BooleanField(verbose_name='Доступна ли только для квал инвесторов')),
                ('exchange', models.CharField(max_length=50, verbose_name='Биржа')),
                ('lot', models.FloatField()),
                ('nominal', models.FloatField()),
                ('country_of_risk', models.CharField(max_length=4, verbose_name='Страна акции')),
                ('sector', models.CharField(max_length=32)),
                ('div_yield_flag', models.BooleanField(verbose_name='Платит ли дивиденды')),
                ('share_type', models.CharField(max_length=10, verbose_name='Тип акции по классификации Тинькоф')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_buy_or_sell', models.BooleanField(choices=[(1, 'Покупка'), (0, 'Продажа')], verbose_name='Операция')),
                ('figi', models.CharField(max_length=16, verbose_name='figi инструмента')),
                ('currency', models.CharField(max_length=16, verbose_name='Валюта покупки')),
                ('price_in_rub', models.FloatField(default=0, verbose_name='Цена на момент покупки в рублях')),
                ('price_in_usd', models.FloatField(default=0, verbose_name='Цена на момент покупки в долларах')),
                ('lot', models.FloatField(verbose_name='Количество актива')),
                ('date_operation', models.DateField(default=datetime.datetime(2023, 9, 17, 16, 22, 49, 779962))),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserStock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('figi', models.CharField(max_length=32, verbose_name='figi инструмента')),
                ('lot', models.FloatField(verbose_name='Количество актива')),
                ('average_price_in_rub', models.FloatField(default=0, verbose_name='Средняя цена в рублях')),
                ('average_price_in_usd', models.FloatField(default=0, verbose_name='Средняя цена в долларах')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
