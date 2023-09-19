from django.shortcuts import render, redirect
from django.views.generic import ListView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.conf import settings

from portfolio.services.add_change_in_user_assets import AssetsChange
from portfolio.services.portfolio import CryptoPortfolio
from .forms import AddCryptoForm, AddCryptoInvestForm
from .models import PersonsCrypto, PersonsTransactions
from .serializers import CryptoTransactionsSerializer
from .tasks import add_transactions_and_update_users_portfolio

from deposits.utils import menu, DataMixin

import logging


logger = logging.getLogger('main')


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
            logger.warning(request.user)
            logger.warning(request.user.id)
            if settings.IN_DOCKER:
                add_transactions_and_update_users_portfolio.delay(assets_type='crypto',
                                                                  user_id=request.user.id,
                                                                  is_buy_or_sell=int(form.data['is_buy_or_sell']),
                                                                  token_1=form.data['token_1'].lower(),
                                                                  token_2=form.data['token_2'].lower(),
                                                                  lot=float(form.data['lot']),
                                                                  price_currency=
                                                                  float(form.data['price_in_currency']),
                                                                  currency='usd',
                                                                  date_operation=form.data['operation_date'])
            else:
                AssetsChange.add_transaction_in_bd_and_update_users_assets(assets_type='crypto',
                                                                           user=request.user,
                                                                           is_buy_or_sell=int(form.data['is_buy_or_sell']),
                                                                           token_1=form.data['token_1'].lower(),
                                                                           token_2=form.data['token_2'].lower(),
                                                                           lot=float(form.data['lot']),
                                                                           price_currency=
                                                                           float(form.data['price_in_currency']),
                                                                           currency='usd',
                                                                           date_operation=form.data['operation_date'])
            return redirect('crypto:add_crypto')
    else:
        form = AddCryptoForm()
    return render(request, 'crypto/add_crypto.html', {'form': form, 'menu': menu})


def add_invest_sum(request):
    if request.method == 'POST':
        form = AddCryptoInvestForm(request.POST)
        if form.is_valid():
            # if settings.IN_DOCKER:
            #     add_transactions_and_update_users_portfolio.delay(assets_type='crypto',
            #                                                       user_id=request.user.id,
            #                                                       is_buy_or_sell=int(form.data['is_buy_or_sell']),
            #                                                       token_1=form.data['token_1'].lower(),
            #                                                       token_2=form.data['token_2'].lower(),
            #                                                       lot=float(form.data['lot']),
            #                                                       price_currency=
            #                                                       float(form.data['price_in_currency']),
            #                                                       currency='usd',
            #                                                       date_operation=form.data['operation_date'])
            # else:
            AssetsChange.add_invest_sum(assets_type='crypto',
                                            invest_sum=float(form.data['invest_sum']),
                                            currency=form.data['currency'],
                                        date_operation=form.data['operation_date'],
                                        user=request.user)
            return redirect('crypto:add_invest')
    else:
        form = AddCryptoInvestForm()
    return render(request, 'crypto/add_invest.html', {'form': form, 'menu': menu})


class CryptoBalance(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        balance = CryptoPortfolio(user=request.user)
        return Response(balance.get_info_about_portfolio_and_assets())  # настроить ввод параметров в функцию


class CryptoAddTransactions(generics.CreateAPIView):
    queryset = PersonsTransactions.objects.all()
    serializer_class = CryptoTransactionsSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CryptoHistoryTransactions(generics.ListAPIView):
    queryset = PersonsTransactions.objects.all()
    serializer_class = CryptoTransactionsSerializer
