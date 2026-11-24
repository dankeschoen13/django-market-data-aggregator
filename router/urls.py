from django.urls import path
from . import views

urlpatterns = [
    path('index/', views.index, name='index_page'),
    path('tickers/active/', views.get_available_tickers, name='get_tickers'),
    path('data/<str:ticker_symbol>/latest/', views.get_latest_metrics, name='get_latest_metrics')
]