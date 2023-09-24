from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, UpdateView
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
logger_debug = logging.getLogger('debug')


class CryptoPersonBalance(ListView, DataMixin):
    model = PersonsCrypto
    template_name = 'crypto/cryptos.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context_from_mixin = self.get_user_context(**kwargs)
        crypto_portfolio = CryptoPortfolio(user=self.request.user, assets=context['object_list'])
        # //TODO зачем два обращения в БД (гет контекст и крипто портфолио) (убрать в портфолио)
        context['balance'] = crypto_portfolio.get_info_about_portfolio()
        context['assets'] = crypto_portfolio.get_info_about_assets()
        return context | context_from_mixin


class PersonCryptoEdit(UpdateView, DataMixin):
    model = PersonsCrypto
    template_name = 'crypto/person_crypto_edit.html'
    fields = ['token', 'lot', 'average_price_in_rub', 'average_price_in_usd']
    success_url = reverse_lazy('crypto:crypto')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context_from_mixin = self.get_user_context(**kwargs)
        return context | context_from_mixin


class PersonCryptoTransaction(ListView, DataMixin):
    model = PersonsTransactions
    paginate_by = 30

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context_from_mixin = self.get_user_context(**kwargs)
        return context | context_from_mixin


class PersonCryptoTransactionEdit(UpdateView, DataMixin):
    model = PersonsTransactions
    template_name = 'crypto/person_crypto_transaction_edit.html'
    fields = ['token_1', 'token_2', 'is_buy_or_sell', 'lot', 'price_in_rub', 'price_in_usd', 'date_operation']
    success_url = reverse_lazy('crypto:person_crypto_transactions')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context_from_mixin = self.get_user_context(**kwargs)
        return context | context_from_mixin

    def form_valid(self, form):
        data = super().form_valid(form)

        transaction = self.get_object()

        # пересчитывает параметры актива в портфеля
        AssetsChange.change_crypto_transaction(transaction)
        return data


def add_transaction(request):
    if request.method == 'POST':
        form = AddCryptoForm(request.POST)
        if form.is_valid():
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
                                                                           is_buy_or_sell=int(
                                                                               form.data['is_buy_or_sell']),
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
                                        invest_sum_in_rub=float(form.data['invest_sum_in_rub']),
                                        invest_sum_in_usd=float(form.data['invest_sum_in_usd']),
                                        date_operation=form.data['operation_date'],
                                        user=request.user)
            return redirect('crypto:add_invest')
    else:
        form = AddCryptoInvestForm()
    return render(request, 'crypto/add_invest.html', {'form': form, 'menu': menu})


# -------------------------------DRF------------------------------------------
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
