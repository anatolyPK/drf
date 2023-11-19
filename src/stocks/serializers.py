from rest_framework import serializers

from .models import UserShare, UserShareTransaction
from portfolio.services.add_change_in_user_assets import AssetsChange


class UserStocksSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserShare
        fields = ["user", "figi", "lot", "average_price"]


class UserTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserShareTransaction
        fields = ["is_buy_or_sell", "figi", "lot", "currency", "price", "date_operation"]

    def create(self, validated_data):
        transaction = UserShareTransaction.objects.create(**validated_data)
        AssetsChange.update_persons_portfolio(transaction=transaction,
                                                  assets_type='stock')
        return transaction
