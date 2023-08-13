from rest_framework import serializers
from .models import PersonsCrypto,  PersonsTransactions


class CryptoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonsCrypto
        fields = '__all__'


class CryptoTransactionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonsTransactions
        fields = '__all__'