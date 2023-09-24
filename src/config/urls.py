"""
URL configuration for investstats project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers

from crypto.urls import crypto_patterns, crypto_patterns_api
from deposits.urls import deposits_patterns, deposits_drf_patterns
from deposits.views import RegisterUser, LoginUser, HomePage, logout_user
from portfolio.urls import portfolio_patterns
from stocks.urls import stocks_patterns, stocks_patterns_api

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/v1/auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),

    path('register/', RegisterUser.as_view(), name='register'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    path('main/', HomePage.as_view(), name='home'),

    path('stocks/', include((stocks_patterns, 'stocks'))),
    path('deposits/', include((deposits_patterns, 'deposits'))),
    path('crypto/', include((crypto_patterns, 'crypto'))),
    path('portfolio/', include((portfolio_patterns, 'portfolio'))),

    path('api/v1/crypto/', include(crypto_patterns_api)),
    path('api/v1/', include(stocks_patterns)),
    path('api/v1/', include(deposits_drf_patterns))

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)