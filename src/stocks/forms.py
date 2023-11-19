from django import forms
from django.core.exceptions import ValidationError

from stocks.models import UserShareTransaction, UserBondTransaction, UserCurrencyTransaction, UserEtfTransaction, Share, Bond, Currency, Etf
from datetime import datetime


class NameModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name + ' ' + obj.ticker


class BondsCalculater(forms.Form):
    CHOICES_TAX = [
        (0, 'Без налога'),
        (13, '13%'),
        (15, '15%'),
    ]

    @staticmethod
    def get_queryset_bond():
        return Bond.objects.all()

    bond_name = NameModelChoiceField(
        label='Название облигации',
        queryset=get_queryset_bond().order_by('name'),
        required=False
    )

    tax_size = forms.ChoiceField(
        label="Размер налога",
        choices=CHOICES_TAX
    )

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data['bond_name']:
            raise ValidationError(
                'Выберите облигацию!',
            )


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
    def get_queryset_share():
        return Share.objects.all()

    @staticmethod
    def get_queryset_bond():
        return Bond.objects.all()

    @staticmethod
    def get_queryset_etf():
        return Etf.objects.all()

    @staticmethod
    def get_queryset_currency():
        return Currency.objects.all()

    names_share = NameModelChoiceField(
        label='Название акции',
        queryset=get_queryset_share().order_by('name'),
        required=False,
    )
    names_bond = NameModelChoiceField(
        label='Название облигации',
        queryset=get_queryset_bond().order_by('name'),
        required=False
    )
    names_etf = NameModelChoiceField(
        label='Название фонда',
        queryset=get_queryset_etf().order_by('name'),
        required=False
    )
    names_currency = NameModelChoiceField(
        label='Название валюты',
        queryset=get_queryset_currency().order_by('name'),
        required=False
    )

    is_buy_or_sell = forms.ChoiceField(
        label="Операция",
        choices=CHOICES_OPERATION_TYPE
    )

    lot = forms.FloatField(label="Количество")
    price_in_currency = forms.FloatField(label='Цена')
    currency = forms.ChoiceField(label='Валюта', choices=CHOICES_CURRENCY)
    operation_date = forms.DateField(label="Дата операции", initial=datetime.now().date)

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data['assets_name'] = self._get_chosen_asset(cleaned_data)

    def _get_chosen_asset(self, cleaned_data):
        dct = {
            'names_share': 'share',
            'names_bond': 'bond',
            'names_etf': 'etf',
            'names_currency': 'currency'
        }
        data_counter = 0
        for name in ('names_share', 'names_bond', 'names_etf', 'names_currency'):
            if cleaned_data[name]:
                asset = cleaned_data[name]
                dct_name = name
                data_counter += 1

        if data_counter == 1:
            return asset, dct[dct_name]

        raise ValidationError(
            'Выберите один актив!',
        )

