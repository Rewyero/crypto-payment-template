"""
URL configuration for coinfuse project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from coinfuse.payments import views as payment_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Django Browser Reload
    path("__reload__/", include("django_browser_reload.urls")),
    
    # Authentication URLs
    path('auth/login/', auth_views.LoginView.as_view(
        template_name='auth/login.html',
        redirect_authenticated_user=True
    ), name='login'),
    path('auth/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('auth/register/', payment_views.register, name='register'),
    
    # Password Reset URLs
    path('auth/password_reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset_form.html',
             email_template_name='registration/password_reset_email.html',
             subject_template_name='registration/password_reset_subject.txt'
         ), 
         name='password_reset'),
    path('auth/password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ), 
         name='password_reset_done'),
    path('auth/reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html'
         ), 
         name='password_reset_confirm'),
    path('auth/reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
    
    # Main app URLs
    path('', payment_views.landing_page, name='landing'),
    path('dashboard/', payment_views.dashboard, name='dashboard'),
    path('payments/', include('coinfuse.payments.urls')),
    path('shop/', include('coinfuse.ecommerce.urls')),
    path('docs/', include('coinfuse.docs.urls')),
    path('support/', payment_views.support, name='support'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ] 