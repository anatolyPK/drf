from django.shortcuts import render, redirect
from django.views.generic import ListView
from rest_framework import generics, viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from deposits.utils import DataMixin, menu
from services.add_change_in_user_assets import AssetsChange
from services.portfolio import StockPortfolio
from .forms import AddStockForm
from .models import UserStock, UserTransaction
from .serializers import UserStocksSerializer, UserTransactionSerializer
from .services.tinkoff_API import TinkoffAPI


class PersonStock(ListView, DataMixin):
    model = UserStock
    template_name = 'stocks/stocks.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context_from_mixin = self.get_user_context(**kwargs)

        stocks_portfolio = StockPortfolio(user=self.request.user)

        context['balance'] = stocks_portfolio.get_info_about_portfolio()
        context['assets'] = stocks_portfolio.get_info_about_assets()

        return context | context_from_mixin


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
        form = AddStockForm(request.POST)
        if form.is_valid():
            selected_asset = form.cleaned_data['names_asset']
            AssetsChange.add_transaction_in_bd_and_update_users_assets(assets_type='stock',
                                               user=request.user,
                                               is_buy_or_sell=int(form.data['is_buy_or_sell']),
                                               figi=selected_asset.figi,
                                               lot=float(form.data['lot']),
                                               price_currency=float(form.data['price_in_currency']),
                                               currency=form.data['currency'],
                                                                       date_operation=form.data['operation_date'])
            return redirect('stocks:add_stock')
    else:
        form = AddStockForm()
    return render(request, 'stocks/add_stock.html', {'form': form, 'menu': menu})


class StockViewSets(viewsets.ViewSet):
    serializer_class = UserStocksSerializer
    permission_classes = (IsAuthenticated,)
    queryset = UserStock.objects.all()

    def list(self, request):
        balance = StockPortfolio(user=request.user)
        return Response(balance.get_info_about_portfolio_and_assets())

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
