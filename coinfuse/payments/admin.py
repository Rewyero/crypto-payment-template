from django.contrib import admin
from .models import APIKey, Payment

@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ('user', 'key', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__username', 'key')
    readonly_fields = ('key', 'created_at')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount_usd', 'crypto_type', 'status', 'created_at')
    list_filter = ('status', 'crypto_type', 'created_at')
    search_fields = ('user__username', 'charge_id')
    readonly_fields = ('created_at', 'updated_at')
