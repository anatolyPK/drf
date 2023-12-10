from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView
from rest_framework import generics, viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from deposits.utils import DataMixinMenu, menu
from portfolio.services.add_change_in_user_assets import AssetsChange
from portfolio.services.config import Stock
from portfolio.services.portfolio import StockPortfolio, PortfolioMaker
from .forms import AddStockForm, BondsCalculater,PortfolioForm
from .models import Share, UserShare, Portfolio, UserShareTransaction, UserBondTransaction, UserEtfTransaction, \
    UserCurrencyTransaction
from .serializers import UserStocksSerializer, UserTransactionSerializer

import logging

from .services.bonds_calculator import BondCalculator
from .utils import DataMixinPortfolio

logger_debug = logging.getLogger('debug')


class PersonStock(ListView, DataMixinMenu, DataMixinPortfolio):
    model = UserShare
    template_name = 'stocks/stocks.html'

    def get_queryset(self):
        portfolio_id = self.kwargs.get('portfolio_id')
        if portfolio_id:
            return UserShare.objects.filter(user=self.request.user, portfolios__id=portfolio_id)

        return UserShare.objects.filter(user=self.request.user)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context_transaction_buttons = self.get_transaction_buttons(**kwargs)
        context_from_mixin_menu = self.get_user_menu(**kwargs)
        context_from_mixin_portfolios = self.get_user_portfolios(self.request.user, **kwargs)

        portfolio_maker = PortfolioMaker(user=self.request.user,
                                         assets_type=Stock,
                                         assets=context['object_list'])
        portfolio = portfolio_maker.portfolio

        context['balance'] = portfolio

        assets = portfolio.get_info_about_assets()
        context['assets'] = assets

        context['shares'] = (asset for asset in assets.values() if asset._stock_tag=='usershare')
        context['bonds'] = (asset for asset in assets.values() if asset._stock_tag=='userbond')
        context['etfs'] = (asset for asset in assets.values() if asset._stock_tag=='useretf')
        context['currencies'] = (asset for asset in assets.values() if asset._stock_tag=='usercurrency')

        context['portfolios'] = Portfolio.objects.filter(user=self.request.user)

        return context | context_from_mixin_menu | context_from_mixin_portfolios | context_transaction_buttons


class PersonStockPortfolio(ListView, DataMixinMenu, DataMixinPortfolio):
    model = UserShare
    template_name = 'stocks/stocks.html'

    def get_queryset(self):
        return UserShare.objects.filter(portfolio=self.kwargs['pk'])

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context_transaction_buttons = self.get_transaction_buttons(**kwargs)
        context_from_mixin_menu = self.get_user_menu(**kwargs)
        context_from_mixin_portfolios = self.get_user_portfolios(self.request.user, **kwargs)
        portfolio_maker = PortfolioMaker(user=self.request.user,
                                         assets_type='stock',
                                         assets=context['object_list'],
                                         is_portfolio=True)
        portfolio = portfolio_maker.portfolio

        context['balance'] = portfolio
        context['assets'] = portfolio.get_info_about_assets()

        return context | context_from_mixin_menu | context_from_mixin_portfolios | context_transaction_buttons


class PersonStockTransaction(ListView, DataMixinMenu, DataMixinPortfolio):
    model = UserShareTransaction
    paginate_by = 20
    ordering = ['-date_operation']
    template_name = 'stocks/stock_transactions_list.html'

    def get_queryset(self):
        user = self.request.user
        models = {
            'share': UserShareTransaction.objects.filter(user=user),
            'bond': UserBondTransaction.objects.filter(user=user),
            'etf': UserEtfTransaction.objects.filter(user=user),
            'currency': UserCurrencyTransaction.objects.filter(user=user),
        }
        queryset = models.get(self.kwargs['assets_type'])
        ordering = self.get_ordering()

        if ordering:
            queryset = queryset.order_by(ordering)

        return queryset

    def get_ordering(self):
        # в балансе можно сделать также, только здесь прописать логику сортировки
        ordering = self.request.GET.get('ordering', '-date_operation')
        return ordering

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context_transaction_buttons = self.get_transaction_buttons(**kwargs)
        context_from_mixin = self.get_user_menu(**kwargs)
        context['assets_type'] = self.kwargs['assets_type']
        return context | context_from_mixin | context_transaction_buttons


class PersonStockTransactionEdit(UpdateView, DataMixinMenu, DataMixinPortfolio):
    template_name = 'stocks/person_stock_transaction_edit.html'
    fields = ['figi', 'is_buy_or_sell', 'lot', 'price_in_rub', 'price_in_usd', 'date_operation']

    def get_success_url(self):
        return reverse_lazy('stocks:transactions', kwargs={'assets_type': self.kwargs['assets_type']})

    def get_model(self):
        models = {
            'share': UserShareTransaction,
            'bond': UserBondTransaction,
            'etf': UserEtfTransaction,
            'currency': UserCurrencyTransaction,
        }
        slug = self.kwargs.get('assets_type')
        return models[slug]

    def get_object(self, queryset=None):
        # Получаем объект на основе выбранной модели
        model = self.get_model()
        return model.objects.get(pk=self.kwargs['pk'])

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context_from_mixin = self.get_user_menu(**kwargs)
        context_transaction_buttons = self.get_transaction_buttons(**kwargs)
        return context | context_from_mixin | context_transaction_buttons

    # def form_valid(self, form):
    #     data = super().form_valid(form)
    #
    #     transaction = self.get_object()
    #
    #     # пересчитывает параметры актива в портфеля
    #     if settings.IN_DOCKER:
    #         update_crypto_transaction.delay(transaction=transaction)
    #     else:
    #         AssetsChange.change_crypto_transaction(changed_transaction=transaction)
    #     return data


#
# class PersonCryptoTransactionDelete(DeleteView, DataMixinMenu):
#     model = PersonsTransactions
#     success_url = reverse_lazy('crypto:person_crypto_transactions')
#     template_name = 'crypto/confirm_delete.html'
#
#     def form_valid(self, form):
#         deleted_object = self.get_object()
#         obj = super().form_valid(form)
#         AssetsChange.change_crypto_transaction(deleted_object)
#         return obj

    # def get_queryset(self):
    #     queryset = PersonsTransactions.objects.filter(user=self.request.user)
    #     ordering = self.get_ordering()
    #
    #     if ordering:
    #         queryset = queryset.order_by(ordering)
    #
    #     return queryset


def add_portfolio(request):
    if request.method == 'POST':
        form = PortfolioForm(request.POST)
        if form.is_valid():
            portfolio = form.save(commit=False)
            portfolio.user = request.user
            portfolio.save()
            return redirect('stocks:stock_portfolio', portfolio_id=portfolio.id)  # Перенаправление на страницу с деталями портфеля
    else:
        form = PortfolioForm()
    return render(request, 'stocks/add_portfolio.html', {'form': form})


def calculate_bond(request):
    selected_asset = None
    if request.method == 'POST':
        form = BondsCalculater(request.POST)
        if form.is_valid():
            asset = form.cleaned_data['bond_name']
            tax_size = form.cleaned_data['tax_size']
            if asset:
                selected_asset = BondCalculator(asset, tax_size=tax_size)
    else:
        form = BondsCalculater()
    return render(request, 'stocks/bonds_calc.html', {'form': form, 'menu': menu, 'selected_asset': selected_asset})


# class PersonTransaction(CreateView, DataMixin):
#     pass
#     form_class = AddStockForm
#     template_name = 'stocks/add_stock.html'
#
#     def get_context_data(self, *, object_list=None, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context_from_mixin = self.get_user_context(**kwargs)
#         context['title'] = 'Добавление актива'
#         return context | context_from_mixin


def add_stock_transaction(request):
    if request.method == 'POST':
        form = AddStockForm(request.user, request.POST)
        if form.is_valid():
            selected_asset, asset_name = form.cleaned_data['assets_name'] #rename asset_name
            AssetsChange.add_transaction_in_bd_and_update_users_assets(assets_type='stock', #можно не передавать все параметры
                                                                       user=request.user,
                                                                       is_buy_or_sell=int(form.data['is_buy_or_sell']),
                                                                       figi=selected_asset.figi,
                                                                       lot=float(form.data['lot']),
                                                                       price_currency=float(
                                                                           form.data['price_in_currency']),
                                                                       currency=form.data['currency'],
                                                                       date_operation=form.data['operation_date'],
                                                                       asset_name=asset_name,
                                                                       asset=selected_asset,
                                                                       portfolios=form.cleaned_data['portfolios'][0])
            return redirect('stocks:add_stock')
    else:
        form = AddStockForm(user=request.user)
    return render(request, 'stocks/add_stock.html', {'form': form, 'menu': menu})


# class StockViewSets(viewsets.ViewSet):
#     serializer_class = UserStocksSerializer
#     permission_classes = (IsAuthenticated,)
#     queryset = UserStock.objects.all()
#
#     def list(self, request):
#         balance = StockPortfolio(user=request.user)
#         return Response(balance.get_info_about_portfolio_and_assets())
#
#     def create(self, request):
#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save(user=self.request.user)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#
#     def partial_update(self, request, pk=None):  # добавить авто подстановку времени ообновления
#         deposit = get_object_or_404(self.queryset, pk=pk)
#         serializer = self.serializer_class(deposit, request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)


# class StockTransactions(generics.CreateAPIView):
#     serializer_class = UserTransactionSerializer
#     permission_classes = (IsAuthenticated,)
#     queryset = UserTransaction.objects.all()
#
#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)
#         return Response(serializer.data)
