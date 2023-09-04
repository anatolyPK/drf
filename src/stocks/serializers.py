from rest_framework import serializers

from .models import UserStock, UserTransaction
from services.add_change_in_portfolio import PersonsPortfolio


class UserStocksSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserStock
        fields = ["user", "figi", "lot", "average_price"]


class UserTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTransaction
        fields = ["is_buy_or_sell", "figi", "lot", "currency", "price", "date_operation"]

    def create(self, validated_data):
        transaction = UserTransaction.objects.create(**validated_data)
        PersonsPortfolio.update_persons_portfolio(transaction=transaction,
                                                  assets_type='stock')
        return transaction
