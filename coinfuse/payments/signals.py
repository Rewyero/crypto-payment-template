from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
from coinfuse.payments.models import Payment, Subscription
from django.contrib.auth.models import User
from decimal import Decimal

@receiver(pre_save, sender=Payment)
def payment_pre_save(sender, instance, **kwargs):
    """Handle payment status changes before saving."""
    if instance.pk:  # If this is an update
        old_instance = Payment.objects.get(pk=instance.pk)
        if old_instance.status != instance.status:
            # Handle status change
            if instance.status == 'completed':
                instance.completed_at = timezone.now()
            elif instance.status == 'failed':
                instance.failed_at = timezone.now()

@receiver(post_save, sender=Payment)
def payment_post_save(sender, instance, created, **kwargs):
    """Handle actions after a payment is saved."""
    if created:
        # New payment created
        pass
    else:
        # Payment updated
        if instance.status == 'completed':
            # Handle successful payment
            subscription = instance.subscription
            if subscription:
                subscription.is_active = True
                subscription.save()
        elif instance.status == 'failed':
            # Handle failed payment
            pass

@receiver(pre_save, sender=Subscription)
def subscription_pre_save(sender, instance, **kwargs):
    """Handle subscription status changes."""
    if instance.pk:
        old_instance = Subscription.objects.get(pk=instance.pk)
        if old_instance.status != instance.status:
            if instance.status == 'active':
                instance.activated_at = timezone.now()
            elif instance.status == 'cancelled':
                instance.cancelled_at = timezone.now()
            elif instance.status == 'expired':
                instance.expired_at = timezone.now()

@receiver(post_save, sender=User)
def create_user_subscription(sender, instance, created, **kwargs):
    """Create a free trial subscription for new users."""
    if created:
        # Create a free trial subscription
        Subscription.objects.create(
            user=instance,
            plan_name='Free Trial',
            amount_usd=Decimal('0.00'),
            crypto_type='BTC',  # Default to Bitcoin
            crypto_amount=Decimal('0.00'),
            interval='monthly',
            status='active',
            next_renewal=timezone.now() + timezone.timedelta(days=30)  # 30-day trial
        ) 