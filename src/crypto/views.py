from django.http import HttpResponse
from rest_framework import generics, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from .crypto_services import PersonsPortfolio
from .models import PersonsCrypto, PersonsTransactions
from .serializers import CryptoSerializer, CryptoTransactionsSerializer, DataSerializer


class CryptoBalance(generics.ListAPIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        balance = PersonsPortfolio(type_of_assets='crypto', person_id=request.user.id)
        return HttpResponse(DataSerializer.serialize_data(balance.returns_info_about_portfolio_and_assets()))


class CryptoAddTransactions(generics.CreateAPIView):
    queryset = PersonsTransactions.objects.all()
    serializer_class = CryptoTransactionsSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(person_id=self.request.user.id)


class CryptoHistoryTransactions(generics.ListAPIView):
    queryset = PersonsTransactions.objects.all()
    serializer_class = CryptoTransactionsSerializer

