from django.http import HttpResponse
from django.shortcuts import get_list_or_404, render, redirect
from django.views.generic import ListView
from rest_framework import generics, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from services.add_change_in_user_assets import AssetsChange
from services.portfolio import PersonsPortfolio, CryptoPortfolio
from .forms import AddCryptoForm
from .models import PersonsCrypto, PersonsTransactions
from .serializers import CryptoSerializer, CryptoTransactionsSerializer, DataSerializer

from deposits.utils import menu, DataMixin


class CryptoPersonBalance(ListView, DataMixin):
    model = PersonsCrypto
    template_name = 'crypto/cryptos.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context_from_mixin = self.get_user_context(**kwargs)

        crypto_portfolio = CryptoPortfolio(user=self.request.user)

        context['balance'] = crypto_portfolio.get_info_about_portfolio()
        context['assets'] = crypto_portfolio.get_info_about_assets()

        return context | context_from_mixin


def add_transaction(request):
    if request.method == 'POST':
        form = AddCryptoForm(request.POST)
        if form.is_valid():
            selected_asset = form.cleaned_data['names_asset']
            AssetsChange.add_transaction_in_bd_and_update_users_assets(assets_type='stock',
                                               user=request.user,
                                               is_buy_or_sell=int(form.data['is_buy_or_sell']),
                                               figi=selected_asset.figi,
                                               lot=float(form.data['lot']),
                                               price_currency=float(form.data['price_in_currency']),
                                               currency=form.data['currency'])
            return redirect('stocks:stocks')
    else:
        form = AddCryptoForm()
    return render(request, 'crypto/add_crypto.html', {'form': form, 'menu': menu})


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

