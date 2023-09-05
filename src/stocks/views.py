from rest_framework import generics, viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from services.portfolio import PersonsPortfolio, StockPortfolio
from .models import UserStock, UserTransaction
from .serializers import UserStocksSerializer, UserTransactionSerializer


class StockViewSets(viewsets.ViewSet):
    serializer_class = UserStocksSerializer
    permission_classes = (IsAuthenticated,)
    queryset = UserStock.objects.all()

    def list(self, request):
        balance = StockPortfolio(user=request.user)
        return Response(balance.returns_info_about_portfolio_and_assets())

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk=None):  #добавить авто подстановку времени ообновления
        deposit = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(deposit, request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class StockTransactions(generics.CreateAPIView):
    serializer_class = UserTransactionSerializer
    permission_classes = (IsAuthenticated,)
    queryset = UserTransaction.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        return Response(serializer.data)
