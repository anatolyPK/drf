

menu = [
    {'title': "Крипто рынок", 'url_name': 'crypto:crypto'},
    {'title': "Фондовый рынок", 'url_name': 'stocks:stocks'},
    {'title': "Вклады", 'url_name': 'deposits:deposits'},
]


class DataMixinMenu:
    def get_user_menu(self, **kwargs):
        context = kwargs
        context['menu'] = menu
        return context

