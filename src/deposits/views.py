from rest_framework import generics, viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from deposits.models import PersonsDeposits, PersonDepositsTransactions
from deposits.serializers import PersonsDepositsSerializer, PersonsDepositsTransactionsSerializer


class DepositsViewSets(viewsets.ViewSet):
    serializer_class = PersonsDepositsSerializer
    permission_classes = (IsAuthenticated,)
    queryset = PersonsDeposits.objects.all()

    def list(self, request):
        queryset = PersonsDeposits.objects.filter(person_id=self.request.user.id)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(person_id=self.request.user.id)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk=None):  #добавить авто подстановку времени ообновления
        deposit = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(deposit, request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class DepositsTransactions(generics.CreateAPIView):
    serializer_class = PersonsDepositsTransactionsSerializer
    permission_classes = (IsAuthenticated,)
    queryset = PersonDepositsTransactions.objects.all()

    def perform_create(self, serializer):
        serializer.save(person_id=self.request.user.id)
        return Response(serializer.data)
