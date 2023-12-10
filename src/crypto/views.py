from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.conf import settings

from portfolio.services.add_change_in_user_assets import AssetsChange
from portfolio.services.portfolio import CryptoPortfolio, PortfolioMaker
from portfolio.services.portfolio_balance import write_in_db_portfolio_balance
from stocks.utils import DataMixinPortfolio
from .forms import AddCryptoForm, AddCryptoInvestForm
from .models import PersonsCrypto, PersonsTransactions
from .serializers import CryptoTransactionsSerializer
from .tasks import add_transactions_and_update_users_portfolio, update_crypto_transaction, add_invest_sum_task

from deposits.utils import menu, DataMixinMenu

import logging

logger = logging.getLogger('main')
logger_debug = logging.getLogger('debug')


class CryptoPersonBalance(ListView, DataMixinMenu, DataMixinPortfolio):
    model = PersonsCrypto
    template_name = 'crypto/cryptos.html'

    def get_queryset(self):
        return PersonsCrypto.objects.filter(user=self.request.user)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context_from_mixin = self.get_user_menu(**kwargs)
        crypto_portfolio_maker = PortfolioMaker(assets_type='crypto', user=self.request.user,
                                                assets=context['object_list'])
        portfolio = crypto_portfolio_maker.portfolio
        context['balance'] = portfolio
        context['assets'] = portfolio.get_info_about_assets()

        return context | context_from_mixin


class PersonCryptoEdit(UpdateView, DataMixinMenu):
    model = PersonsCrypto
    template_name = 'crypto/person_crypto_edit.html'
    fields = ['token', 'lot', 'average_price_in_rub', 'average_price_in_usd']
    success_url = reverse_lazy('crypto:crypto')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context_from_mixin = self.get_user_menu(**kwargs)
        return context | context_from_mixin


class PersonCryptoTransaction(ListView, DataMixinMenu):
    model = PersonsTransactions
    paginate_by = 20
    ordering = ['-date_operation']

    def get_queryset(self):
        queryset = PersonsTransactions.objects.filter(user=self.request.user)
        ordering = self.get_ordering()

        if ordering:
            queryset = queryset.order_by(ordering)

        return queryset

    def get_ordering(self):
        # в балансе можно сделать также, тольок здесь прописать логику сортировки
        ordering = self.request.GET.get('ordering', '-date_operation')
        logger_debug.debug(ordering)
        return ordering

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context_from_mixin = self.get_user_menu(**kwargs)
        return context | context_from_mixin


class PersonCryptoTransactionEdit(UpdateView, DataMixinMenu):
    model = PersonsTransactions
    template_name = 'crypto/person_crypto_transaction_edit.html'
    fields = ['token_1', 'token_2', 'is_buy_or_sell', 'lot', 'price_in_rub', 'price_in_usd', 'date_operation']
    success_url = reverse_lazy('crypto:person_crypto_transactions')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context_from_mixin = self.get_user_menu(**kwargs)
        return context | context_from_mixin

    def form_valid(self, form):
        data = super().form_valid(form)

        transaction = self.get_object()

        # пересчитывает параметры актива в портфеля
        if settings.IN_DOCKER:
            update_crypto_transaction.delay(transaction=transaction)
        else:
            AssetsChange.change_crypto_transaction(changed_transaction=transaction)
        return data


class PersonCryptoTransactionDelete(DeleteView, DataMixinMenu):
    model = PersonsTransactions
    success_url = reverse_lazy('crypto:person_crypto_transactions')
    template_name = 'crypto/confirm_delete.html'

    def form_valid(self, form):
        deleted_object = self.get_object()
        obj = super().form_valid(form)
        AssetsChange.change_crypto_transaction(deleted_object)
        return obj


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
                                                                           is_buy_or_sell=
                                                                           int(form.data['is_buy_or_sell']),
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
            if settings.IN_DOCKER:
                add_invest_sum_task.delay(invest_sum_in_rub=float(form.data['invest_sum_in_rub']),
                                          invest_sum_in_usd=float(form.data['invest_sum_in_usd']),
                                          date_operation=form.data['operation_date'],
                                          user_id=request.user.id)
            else:
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
