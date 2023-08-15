from django.http import HttpResponse
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated
from services import get_portfolio
from .models import PersonsCrypto, PersonsTransactions
from .serializers import CryptoSerializer, CryptoTransactionsSerializer


class CryptoBalance(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        data = PersonsCrypto.objects.all().filter(person_id=self.request.user.id)
        return HttpResponse(get_portfolio(personal_assets=data, is_crypto=True))

    # serializer_class = CryptoSerializer
    # permission_classes = (IsAuthenticated, )
    #
    # def get_queryset(self):
    #     data = PersonsCrypto.objects.all().filter(person_id=self.request.user.id)
    #     return get_portfolio(personal_assets=data, is_crypto=True)
    #     # print(portfolio.total_balance)
        # print(portfolio.get_portfolio_profit())


class CryptoAddTransactions(generics.CreateAPIView):
    queryset = PersonsTransactions.objects.all()
    serializer_class = CryptoTransactionsSerializer


class CryptoHistoryTransactions(generics.ListAPIView):
    queryset = PersonsTransactions.objects.all()
    serializer_class = CryptoTransactionsSerializer

