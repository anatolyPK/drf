

menu = [
    {'title': "Профиль", 'url_name': 'home'},
    {'title': "Крипто рынок", 'url_name': 'crypto:crypto'},
    {'title': "Фондовый рынок", 'url_name': 'stocks:stocks'},
    {'title': "Вклады", 'url_name': 'deposits:deposits'},
]


class DataMixin:
    def get_user_context(self, **kwargs):
        context = kwargs
        context['menu'] = menu
        return context
