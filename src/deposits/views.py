from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, get_list_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView
from rest_framework import generics, viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from deposits.forms import RegisterUserForm, LoginUserForm
from deposits.models import PersonsDeposits, PersonDepositsTransactions
from deposits.serializers import PersonsDepositsSerializer, PersonsDepositsTransactionsSerializer
from .utils import menu, DataMixin


#-----------------------DJANGO______________________________
class HomePage(DataMixin, ListView):
    template_name = 'base.html'
    model = PersonsDeposits

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_context = self.get_user_context(title='Главная страница')
        return context | user_context


class RegisterUser(DataMixin, CreateView):
    form_class = RegisterUserForm
    template_name = 'deposits/register.html'
    success_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_context = self.get_user_context(title='Регистрация')
        return context | user_context

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('home')


class LoginUser(DataMixin, LoginView):
    form_class = LoginUserForm
    template_name = 'deposits/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_context = self.get_user_context(title='Авторизация')
        return context | user_context

    def get_success_url(self):
        return reverse_lazy('home')


def logout_user(request):
    logout(request)
    return redirect('login')





def persons_deposits(request):
    deposits = get_list_or_404(PersonsDeposits, user=request.user)
    return render(request, 'deposits/deposits.html', {'deposits': deposits, 'menu': menu})



#----------------------DRF__________________________________
class DepositsViewSets(viewsets.ViewSet):
    serializer_class = PersonsDepositsSerializer
    permission_classes = (IsAuthenticated,)
    queryset = PersonsDeposits.objects.all()

    def list(self, request):
        queryset = PersonsDeposits.objects.filter(user=request.user)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

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


class DepositsTransactions(generics.CreateAPIView):
    serializer_class = PersonsDepositsTransactionsSerializer
    permission_classes = (IsAuthenticated,)
    queryset = PersonDepositsTransactions.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        return Response(serializer.data)
