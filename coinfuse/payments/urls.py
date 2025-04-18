from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('create/', views.create_payment, name='create_payment'),
    path('api/crypto-price/<str:crypto_type>/', views.get_crypto_price_api, name='crypto_price_api'),
    path('api/payments/create/', views.create_payment_api, name='create_payment_api'),
    path('api/volume-data/', views.get_volume_data, name='volume_data'),
    path('api/payments/<int:payment_id>/', views.get_payment_details, name='payment_details'),
    path('webhook/', views.webhook, name='webhook'),
    path('subscriptions/create/', views.create_subscription, name='create_subscription'),
    path('subscriptions/', views.manage_subscriptions, name='manage_subscriptions'),
    path('subscriptions/<int:subscription_id>/cancel/', views.cancel_subscription, name='cancel_subscription'),
    path('connect-wallet/', views.connect_wallet, name='connect_wallet'),
    path('manage-wallets/', views.manage_wallets, name='manage_wallets'),
    path('manage-wallets/<int:wallet_id>/delete/', views.delete_wallet, name='delete_wallet'),
    path('transactions/', views.transaction_history, name='transaction_history'),
    path('api/transactions/', views.api_transactions, name='api_transactions'),
    path('api-keys/', views.manage_api_keys, name='api_keys'),
] 