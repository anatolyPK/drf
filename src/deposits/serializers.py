from rest_framework import serializers

from .models import PersonsDeposits, PersonDepositsTransactions
from .services import add_or_take_sum_from_deposit


class PersonsDepositsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonsDeposits
        fields = ["id", "deposits_summ", "description", "percent", "percent_capitalization", "date_open"]


class PersonsDepositsTransactionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonDepositsTransactions
        fields = ['deposit_id', 'is_add_or_take', 'size', 'date_operation']

    def create(self, validated_data):
        transaction = PersonDepositsTransactions.objects.create(**validated_data)
        add_or_take_sum_from_deposit(transaction)
        return transaction