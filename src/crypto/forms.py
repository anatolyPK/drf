from datetime import datetime

from django import forms
from django.core.cache import cache
import logging


logger_debug = logging.getLogger('debug')


class NameModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name + ' ' + obj.ticker


class AddCryptoForm(forms.Form):
    CHOICES_OPERATION_TYPE = [
        (1, 'Покупка'),
        (0, 'Продажа'),
    ]

    token_1 = forms.CharField(label='Первый токен', max_length=6)
    token_2 = forms.CharField(label='Второй токен', max_length=6, initial='USDT', help_text='Если ')
    is_buy_or_sell = forms.ChoiceField(label="Операция", choices=CHOICES_OPERATION_TYPE)
    price_in_currency = forms.FloatField(label='Цена')
    lot = forms.FloatField(label="Количество")
    operation_date = forms.DateField(label="Дата операции",
                                     initial=datetime.now().date,
                                     )

    def clean(self):
        cleaned_data = super().clean()
        token_1 = cleaned_data.get('token_1').upper()
        token_2 = cleaned_data.get('token_2').upper()

        if not (cache.get(f'{token_1}{token_2}')):
            raise forms.ValidationError("Проверьте токены!")


class AddCryptoInvestForm(forms.Form):
    CHOICES_CURRENCY = [
        ('rub', 'Руб'),
        ('usd', 'Usd'),
    ]

    invest_sum_in_rub = forms.FloatField(label='Сумма вложений в рублях')
    invest_sum_in_usd = forms.FloatField(label='Сумма вложений в долларах')
    operation_date = forms.DateField(label="Дата операции",
                                     initial=datetime.now().date,
                                     )

    def clean_operation_date(self):
        data = self.cleaned_data['operation_date']



