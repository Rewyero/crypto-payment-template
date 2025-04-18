from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum, Count
from django.http import JsonResponse
from datetime import timedelta
from coinfuse.payments.models import Payment, Subscription
import json

@login_required
def checkout(request):
    # Sample product data - replace with your actual product logic
    product = {
        'name': 'Premium Plan',
        'description': 'Access to all premium features',
        'price': 100.00,
        'features': [
            'Unlimited access to all features',
            'Priority support',
            'Custom branding',
            'API access'
        ]
    }
    
    return render(request, 'ecommerce/checkout.html', {
        'product': product
    })

@login_required
def get_transaction_volume(request):
    days = int(request.GET.get('days', 30))
    now = timezone.now()
    start_date = now - timedelta(days=days)
    
    # Get daily transaction volumes
    daily_volumes = Payment.objects.filter(
        user=request.user,
        created_at__gte=start_date,
        created_at__lte=now
    ).values('created_at__date').annotate(
        total=Sum('amount_usd')
    ).order_by('created_at__date')
    
    # Fill in missing dates with zero values
    dates = []
    values = []
    current_date = start_date.date()
    volume_dict = {item['created_at__date']: float(item['total']) for item in daily_volumes}
    
    while current_date <= now.date():
        dates.append(current_date.strftime('%b %d'))
        values.append(volume_dict.get(current_date, 0))
        current_date += timedelta(days=1)
    
    return JsonResponse({
        'labels': dates,
        'values': values
    })

@login_required
def ecommerce_dashboard(request):
    # Get user's payment and subscription data
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    subscriptions = Subscription.objects.filter(user=request.user)
    
    context = {
        'payments': payments,
        'subscriptions': subscriptions,
    }
    return render(request, 'ecommerce/ecommerce_dashboard.html', context) 