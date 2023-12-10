from django.contrib import admin
from .models import UserShare, Portfolio, UserEtf, UserCurrency, UserBond

admin.site.register(UserShare)
admin.site.register(UserBond)
admin.site.register(UserCurrency)
admin.site.register(UserEtf)
admin.site.register(Portfolio)
