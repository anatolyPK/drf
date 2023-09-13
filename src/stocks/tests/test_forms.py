from django.test import TestCase, Client
from stocks.models import UserTransaction, Share
from stocks.forms import AddStockForm, NameModelChoiceField
from datetime import datetime


class AddStockFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = AddStockForm()

    def test_field_names_asset_label(self):
        self.assertTrue(self.form.fields['names_asset'].label is None or
                        self.form.fields['names_asset'].label == 'Название бумаги')

    def test_field_names_asset_queryset(self):
        Share.objects.create(figi='BBG00Y9WVZ76',
                             ticker='9992',
                             name='Pop Mart',
                             buy_available_flag=True,
                             currency='usd', sell_available_flag=True,
                             for_iis_flag=True,
                             for_qual_investor_flag=True,
                             exchange='spb',
                             lot=1,
                             nominal=0.1,
                             country_of_risk='ru',
                             sector='fin',
                             div_yield_flag=True,
                             share_type='e'
                             )
        Share.objects.create(figi='B21312r',
                             ticker='eafs',
                             name='PMart',
                             buy_available_flag=True,
                             currency='usd', sell_available_flag=True,
                             for_iis_flag=True,
                             for_qual_investor_flag=True,
                             exchange='spb',
                             lot=1,
                             nominal=0.1,
                             country_of_risk='ru',
                             sector='fin',
                             div_yield_flag=True,
                             share_type='e'
                             )
        queryset = Share.objects.all().order_by('name')
        form_queryset = self.form.fields['names_asset'].queryset
        self.assertEqual(form_queryset[0], queryset[0])
        self.assertEqual(form_queryset[1], queryset[1])

    def test_field_is_buy_or_sell(self):
        choices_operation_type = [
            (1, 'Покупка'),
            (0, 'Продажа'),
        ]
        self.assertEqual(self.form.fields['is_buy_or_sell'].choices, choices_operation_type)

    def test_field_currency(self):
        choices_currency = [
            ('usd', 'USD'),
            ('rub', 'RUB'),
        ]
        self.assertEqual(self.form.fields['currency'].choices, choices_currency)

    def test_field_operation_date(self):
        date_now = datetime.now().date()
        self.assertEqual(self.form.fields['operation_date'].initial(), date_now)


class NameModelChoiceFieldTest(TestCase):
    def test_label_from_instance(self):
        Share.objects.create(figi='BBG00Y9WVZ76',
                             ticker='9992',
                             name='Pop Mart',
                             buy_available_flag=True,
                             currency='usd', sell_available_flag=True,
                             for_iis_flag=True,
                             for_qual_investor_flag=True,
                             exchange='spb',
                             lot=1,
                             nominal=0.1,
                             country_of_risk='ru',
                             sector='fin',
                             div_yield_flag=True,
                             share_type='e'
                             )
        Share.objects.create(figi='B21312r',
                             ticker='eafs',
                             name='PMart',
                             buy_available_flag=True,
                             currency='usd', sell_available_flag=True,
                             for_iis_flag=True,
                             for_qual_investor_flag=True,
                             exchange='spb',
                             lot=1,
                             nominal=0.1,
                             country_of_risk='ru',
                             sector='fin',
                             div_yield_flag=True,
                             share_type='e'
                             )
        obj = Share.objects.all()
        self.assertEqual(NameModelChoiceField(obj).label_from_instance(obj[0]), 'Pop Mart 9992')
        self.assertEqual(NameModelChoiceField(obj).label_from_instance(obj[1]), 'PMart eafs')
