from datetime import datetime

from django import forms

from stocks.models import UserTransaction, Share, Bond


class NameModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name + ' ' + obj.ticker


class AddCryptoForm(forms.Form):
    CHOICES_OPERATION_TYPE = [
        (1, 'Покупка'),
        (0, 'Продажа'),
    ]

    DEFAULT_TOKEN_2 = 'USDT'

    token_1 = forms.CharField(label='Первый токен', max_length=6)
    token_2 = forms.CharField(label='Второй токен', max_length=6, initial='USDT', help_text='Если ')
    is_buy_or_sell = forms.ChoiceField(label="Операция", choices=CHOICES_OPERATION_TYPE)
    price_in_currency = forms.FloatField(label='Цена')
    lot = forms.FloatField(label="Количество")
    operation_date = forms.DateField(label="Дата операции", initial=datetime.now().date)