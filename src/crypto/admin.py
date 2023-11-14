from django.contrib import admin
from .models import PersonsCrypto, CryptoPortfolioBalance, CryptoInvest, PersonsTransactions

admin.site.register(PersonsCrypto)
admin.site.register(CryptoPortfolioBalance)
admin.site.register(CryptoInvest)
admin.site.register(PersonsTransactions)
