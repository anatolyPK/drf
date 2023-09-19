from django.views.generic import ListView

from deposits.utils import DataMixin
from portfolio.models import Portfolio
# from portfolio.services.portfolio import UsersPortfolio


class UserPortfolio(ListView, DataMixin):
    model = Portfolio
    template_name = 'portfolio/portfolio.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_context = self.get_user_context(title='Портфели')

        portfolio = Portfolio.objects.all().first()

        # UsersPortfolio.get_portfolio(portfolio)
        return context | user_context
