from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import PersonsCrypto, PersonsTransactions
from .serializers import CryptoSerializer, CryptoTransactionsSerializer


class CryptoBalance(generics.ListAPIView):
    # queryset = PersonsCrypto.objects.all()
    serializer_class = CryptoSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        user_id = self.request.user.id
        return PersonsCrypto.objects.all().filter(person_id=user_id)


class CryptoAddTransactions(generics.CreateAPIView):
    queryset = PersonsTransactions.objects.all()
    serializer_class = CryptoTransactionsSerializer


class CryptoHistoryTransactions(generics.ListAPIView):
    queryset = PersonsTransactions.objects.all()
    serializer_class = CryptoTransactionsSerializer

