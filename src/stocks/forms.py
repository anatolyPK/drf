from django import forms
from django.core.exceptions import ValidationError

from itertools import chain

from config import settings
from stocks.models import UserTransaction, Share, Bond


class NameModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name + ' ' + obj.ticker


class AddStockForm(forms.Form):
    CHOICES_OPERATION_TYPE = [
        (1, 'Покупка'),
        (0, 'Продажа'),
    ]

    CHOICES_CURRENCY = [
        ('usd', 'USD'),
        ('rub', 'RUB'),
    ]

    @staticmethod
    def get_queryset():
        return Share.objects.all()

    names_asset = NameModelChoiceField(label='Название бумаги',
                                       queryset=get_queryset().order_by('name'))
    is_buy_or_sell = forms.ChoiceField(label="Операция", choices=CHOICES_OPERATION_TYPE)
    lot = forms.FloatField(label="Количество")
    price_in_currency = forms.FloatField(label='Цена')
    currency = forms.ChoiceField(label='Валюта', choices=CHOICES_CURRENCY)