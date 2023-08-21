from django.http import HttpResponse
from rest_framework import generics, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from .services import get_portfolio
from .models import PersonsCrypto, PersonsTransactions
from .serializers import CryptoSerializer, CryptoTransactionsSerializer, DataSerializer


class CryptoBalance(generics.ListAPIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        balance = get_portfolio(user_id=self.request.user.id, is_crypto=True)
        return HttpResponse(DataSerializer.serialize_data(balance))


class CryptoAddTransactions(generics.CreateAPIView):
    queryset = PersonsTransactions.objects.all()
    serializer_class = CryptoTransactionsSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(person_id=self.request.user.id)


class CryptoHistoryTransactions(generics.ListAPIView):
    queryset = PersonsTransactions.objects.all()
    serializer_class = CryptoTransactionsSerializer

