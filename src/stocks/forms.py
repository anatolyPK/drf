from django import forms

from stocks.models import UserTransaction


class AddStockForm(forms.ModelForm):
    class Meta:
        model = UserTransaction
        fields = '__all__'
