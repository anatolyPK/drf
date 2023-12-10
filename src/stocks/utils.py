from stocks.models import Portfolio


class DataMixinPortfolio:
    def get_user_portfolios(self, user, **kwargs):
        context = kwargs
        context['portfolios'] = Portfolio.objects.filter(user=user)
        return context

    def get_transaction_buttons(self, **kwargs):
        context = kwargs
        context['share'] = 'share'
        context['bond'] = 'bond'
        context['etf'] = 'etf'
        context['currency'] = 'currency'
        return context
