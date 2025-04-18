from django.urls import path
from . import views

app_name = 'docs'

urlpatterns = [
    path('', views.docs_home, name='home'),
    path('getting-started/', views.getting_started, name='getting_started'),
    path('api-reference/', views.api_reference, name='api_reference'),
    path('webhooks/', views.webhooks, name='webhooks'),
    path('sdks/', views.sdks, name='sdks'),
    path('examples/', views.examples, name='examples'),
    path('changelog/', views.changelog, name='changelog'),
    path('faq/', views.faq, name='faq'),
] 