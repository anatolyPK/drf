from django.http import HttpResponse
from django.shortcuts import get_list_or_404, render
from rest_framework import generics, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from services.portfolio import PersonsPortfolio, CryptoPortfolio
from .models import PersonsCrypto, PersonsTransactions
from .serializers import CryptoSerializer, CryptoTransactionsSerializer, DataSerializer

from deposits.utils import menu


def persons_crypto(request):
    crypto_portfolio = CryptoPortfolio(user=request.user)
    context = {'balance': crypto_portfolio.get_info_about_portfolio(),
               'assets': crypto_portfolio.get_info_about_assets(),
               'menu': menu
               }
    return render(request, 'crypto/cryptos.html', context)


class CryptoBalance(generics.ListAPIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        balance = CryptoPortfolio(user=request.user)
        return Response(balance.get_info_about_portfolio_and_assets()) #настроить ввод параметров в функцию


class CryptoAddTransactions(generics.CreateAPIView):
    queryset = PersonsTransactions.objects.all()
    serializer_class = CryptoTransactionsSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CryptoHistoryTransactions(generics.ListAPIView):
    queryset = PersonsTransactions.objects.all()
    serializer_class = CryptoTransactionsSerializer

