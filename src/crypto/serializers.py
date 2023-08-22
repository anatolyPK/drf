from rest_framework import serializers
from rest_framework.renderers import JSONRenderer

from .services import add_change_in_persons_portfolio, add_reverse_transaction
from .models import PersonsCrypto,  PersonsTransactions


class CryptoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonsCrypto
        fields = '__all__'


class CryptoTransactionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonsTransactions
        fields = ['is_buy_or_sell', 'token_1',  'token_2', 'price', 'lot']

    def create(self, validated_data):
        transaction = PersonsTransactions.objects.create(**validated_data)
        add_reverse_transaction(**validated_data)
        add_change_in_persons_portfolio(transaction)
        return transaction


class DataSerializer:
    @staticmethod
    def serialize_data(data: dict) -> JSONRenderer:
        return JSONRenderer().render(data)
