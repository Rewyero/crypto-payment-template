from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'coinfuse.payments'
    verbose_name = 'Payments'

    def ready(self):
        import coinfuse.payments.signals
