from django.urls import path
from . import views

app_name = 'ecommerce'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('dashboard/', views.ecommerce_dashboard, name='ecommerce_dashboard'),
    path('api/transactions/volume/', views.get_transaction_volume, name='transaction_volume'),
] 