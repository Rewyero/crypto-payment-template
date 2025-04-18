from django.shortcuts import render, redirect, get_object_or_404
import json
from decimal import Decimal
import requests
import hmac
import hashlib
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib import messages
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Payment, APIKey, Subscription, UserWallet
from django.conf import settings
from django.db import models
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Sum, Count, Case, When, F
from django.utils import timezone
from datetime import timedelta
import uuid
from django.core.exceptions import ValidationError
from .forms import WalletForm
from rest_framework import status

from coinfuse.payments.models import Payment as CryptoPayment
from coinfuse.payments.forms import PaymentForm, SubscriptionForm
from coinfuse.payments.utils import get_crypto_price

def landing_page(request):
    """Display the landing page for non-authenticated users."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'landing.html', {
        'hide_navbar': True,
        'allow_anonymous': True
    })

@login_required
def dashboard(request):
    """
    Display the main dashboard with payment statistics and charts.
    """
    now = timezone.now()
    last_month = now - timedelta(days=30)
    
    # Get payment statistics with proper null handling
    total_orders = CryptoPayment.objects.filter(user=request.user).count()
    total_revenue = CryptoPayment.objects.filter(user=request.user).aggregate(
        total=Sum('amount_usd')
    )['total'] or 0
    
    # Calculate growth percentages with proper zero handling
    last_month_orders = CryptoPayment.objects.filter(
        user=request.user,
        created_at__lt=now,
        created_at__gte=last_month
    ).count()
    previous_month_orders = CryptoPayment.objects.filter(
        user=request.user,
        created_at__lt=last_month,
        created_at__gte=last_month - timedelta(days=30)
    ).count()

    # Prevent division by zero and handle growth calculation
    if previous_month_orders > 0:
        order_growth = ((last_month_orders - previous_month_orders) / previous_month_orders * 100)
    else:
        order_growth = last_month_orders * 100 if last_month_orders > 0 else 0
    
    # Get crypto payment statistics
    crypto_payments = CryptoPayment.objects.filter(
        user=request.user,
        status='completed'
    ).count()
    
    # Calculate crypto growth
    last_month_crypto = CryptoPayment.objects.filter(
        user=request.user,
        status='completed',
        created_at__gte=last_month
    ).count()
    previous_month_crypto = CryptoPayment.objects.filter(
        user=request.user,
        status='completed',
        created_at__lt=last_month,
        created_at__gte=last_month - timedelta(days=30)
    ).count()
    
    if previous_month_crypto > 0:
        crypto_growth = ((last_month_crypto - previous_month_crypto) / previous_month_crypto * 100)
    else:
        crypto_growth = last_month_crypto * 100 if last_month_crypto > 0 else 0

    # Get active subscriptions and calculate growth
    active_subscriptions = Subscription.objects.filter(
        user=request.user,
        status='active'
    ).count()

    last_month_subs = Subscription.objects.filter(
        user=request.user,
        status='active',
        created_at__gte=last_month
    ).count()
    previous_month_subs = Subscription.objects.filter(
        user=request.user,
        status='active',
        created_at__lt=last_month,
        created_at__gte=last_month - timedelta(days=30)
    ).count()
    
    if previous_month_subs > 0:
        subscription_growth = ((last_month_subs - previous_month_subs) / previous_month_subs * 100)
    else:
        subscription_growth = last_month_subs * 100 if last_month_subs > 0 else 0
    
    # Get transaction volume data with proper date handling
    start_date = now - timedelta(days=30)
    daily_volumes = CryptoPayment.objects.filter(
        user=request.user,
        created_at__gte=start_date,
        status='completed'  # Only include completed payments
    ).values('created_at__date').annotate(
        total=Sum('amount_usd')
    ).order_by('created_at__date')
    
    # Ensure consistent date format and handle missing dates
    dates = []
    values = []
    current_date = start_date.date()
    volume_dict = {item['created_at__date']: float(item['total'] or 0) for item in daily_volumes}
    
    while current_date <= now.date():
        dates.append(current_date.strftime('%Y-%m-%d'))  # Use consistent date format
        values.append(round(volume_dict.get(current_date, 0), 2))  # Round to 2 decimal places
        current_date += timedelta(days=1)
    
    # Get payment methods distribution with proper ordering
    payment_methods = CryptoPayment.objects.filter(
        user=request.user,
        status='completed'
    ).values('crypto_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    payment_methods_labels = []
    payment_methods_data = []
    
    # Ensure we have at least one payment method
    if payment_methods:
        payment_methods_labels = [pm['crypto_type'] for pm in payment_methods]
        payment_methods_data = [pm['count'] for pm in payment_methods]
    else:
        # Provide default data to prevent empty chart
        payment_methods_labels = ['No payments']
        payment_methods_data = [0]
    
    # Get recent orders with proper null handling
    recent_orders = []
    for order in CryptoPayment.objects.filter(user=request.user).order_by('-created_at')[:10]:
        recent_orders.append({
            'id': order.id,
            'customer_name': order.user.get_full_name() or order.user.username,
            'product_name': order.description or 'Product Purchase',
            'amount': round(float(order.amount_usd or 0), 2),
            'payment_method': order.crypto_type or 'Unknown',
            'status': order.status or 'pending'
        })
    
    context = {
        'total_orders': total_orders,
        'total_revenue': round(float(total_revenue), 2),
        'order_growth': round(order_growth, 1),
        'crypto_payments': crypto_payments,
        'crypto_growth': round(crypto_growth, 1),
        'active_subscriptions': active_subscriptions,
        'subscription_growth': round(subscription_growth, 1),
        'recent_orders': recent_orders,
        'revenue_labels': json.dumps(dates),
        'revenue_data': json.dumps(values),
        'payment_methods_labels': json.dumps(payment_methods_labels),
        'payment_methods_data': json.dumps(payment_methods_data)
    }
    
    return render(request, 'payments/dashboard.html', context)

@login_required
def get_volume_data(request):
    days = int(request.GET.get('days', 30))
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    daily_volumes = []
    dates = []
    current_date = start_date
    while current_date <= end_date:
        daily_total = Payment.objects.filter(
            user=request.user,
            created_at__date=current_date.date()
        ).aggregate(total=Sum('amount_usd'))['total'] or 0
        daily_volumes.append(float(daily_total))
        dates.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)
    
    return JsonResponse({
        'dates': dates,
        'volumes': daily_volumes
    })

@login_required
def get_payment_details(request, payment_id):
    try:
        payment = Payment.objects.get(id=payment_id, user=request.user)
        return JsonResponse({
            'id': payment.id,
            'created_at': payment.created_at.isoformat(),
            'amount': float(payment.amount_usd),
            'crypto_type': payment.crypto_type,
            'crypto_amount': float(payment.crypto_amount),
            'status': payment.status,
            'wallet_address': payment.wallet_address if hasattr(payment, 'wallet_address') else None
        })
    except Payment.DoesNotExist:
        return JsonResponse({'error': 'Payment not found'}, status=404)

@login_required
def manage_wallets(request):
    if request.method == 'POST':
        wallet_id = request.POST.get('wallet_id')
        
        if wallet_id:
            # Edit existing wallet
            try:
                wallet = UserWallet.objects.get(id=wallet_id, user=request.user)
                form = WalletForm(request.POST, instance=wallet)
            except UserWallet.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'errors': {'wallet_id': ['Wallet not found']}
                }, status=404)
        else:
            # Create new wallet
            form = WalletForm(request.POST)
        
        if form.is_valid():
            wallet = form.save(commit=False)
            wallet.user = request.user
            
            try:
                wallet.clean()  # Run model validation
                wallet.save()
                return JsonResponse({
                    'success': True,
                    'message': 'Wallet updated successfully' if wallet_id else 'Wallet added successfully'
                })
            except ValidationError as e:
                return JsonResponse({
                    'success': False,
                    'errors': e.message_dict
                })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
    
    # Get wallets and serialize them for the template and JavaScript
    wallets = UserWallet.objects.filter(user=request.user).order_by('-created_at')
    serialized_wallets = []
    
    for wallet in wallets:
        serialized_wallets.append({
            'id': wallet.id,
            'crypto_type': wallet.crypto_type,
            'wallet_source': wallet.wallet_source,
            'network': wallet.network,
            'wallet_address': wallet.wallet_address,
            'memo': wallet.memo,
            'is_active': wallet.is_active
        })
    
    # Get valid networks for each crypto type
    crypto_networks = UserWallet.CRYPTO_NETWORK_MAP
    platform_networks = UserWallet.PLATFORM_NETWORK_MAP
    
    context = {
        'wallets': wallets,  # For template rendering
        'wallets_json': json.dumps(serialized_wallets),  # For JavaScript
        'crypto_networks': json.dumps(crypto_networks),
        'platform_networks': json.dumps(platform_networks),
    }
    
    return render(request, 'payments/manage_wallets.html', context)

@login_required
def create_payment(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.user = request.user
            
            # Get current crypto price
            crypto_price = get_crypto_price(payment.crypto_type.lower())
            if crypto_price is None:
                messages.error(request, 'Failed to fetch crypto price. Please try again.')
                return redirect('create_payment')
            
            payment.crypto_amount = payment.amount_usd / Decimal(str(crypto_price))
            payment.save()
            
            # Create Coinbase Commerce charge
            headers = {
                'X-CC-Api-Key': settings.COINBASE_API_KEY,
                'X-CC-Version': '2018-03-22'
            }
            
            payload = {
                'name': f'Payment #{payment.id}',
                'description': f'Payment for {request.user.username}',
                'local_price': {
                    'amount': str(payment.amount_usd),
                    'currency': 'USD'
                },
                'pricing_type': 'fixed_price',
                'metadata': {
                    'payment_id': payment.id
                }
            }
            
            response = requests.post(
                'https://api.commerce.coinbase.com/charges',
                headers=headers,
                json=payload
            )
            
            if response.status_code == 201:
                charge_data = response.json()['data']
                payment.charge_id = charge_data['id']
                payment.hosted_url = charge_data['hosted_url']
                payment.save()
                return redirect(payment.hosted_url)
            else:
                messages.error(request, 'Failed to create payment. Please try again.')
                return redirect('create_payment')
    else:
        form = PaymentForm()
    return render(request, 'payments/create_payment.html', {'form': form})

@login_required
def get_wallet_networks(request):
    crypto_type = request.GET.get('crypto_type')
    wallet_source = request.GET.get('wallet_source', 'Manual')
    
    if wallet_source in ['Revolut', 'Bybit']:
        networks = UserWallet.PLATFORM_NETWORK_MAP[wallet_source].get(crypto_type, [])
    else:
        networks = UserWallet.CRYPTO_NETWORK_MAP.get(crypto_type, [])
    
    return JsonResponse({
        'networks': networks
    })

@api_view(['GET'])
def get_crypto_price_api(request, crypto_type):
    """API endpoint to get current crypto price."""
    # Handle stablecoins
    if crypto_type in ['USDT', 'USDC']:
        return Response({'price': 1.0})
        
    price = get_crypto_price(crypto_type)
    if price:
        return Response({'price': float(price)})
    return Response({'error': 'Error fetching price'}, status=400)

@csrf_exempt
@require_POST
def webhook(request):
    # Verify webhook signature
    signature = request.headers.get('X-CC-Webhook-Signature', '')
    secret = settings.COINBASE_WEBHOOK_SECRET
    body = request.body.decode('utf-8')
    
    expected_sig = hmac.new(
        secret.encode('utf-8'),
        body.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, expected_sig):
        return JsonResponse({'error': 'Invalid signature'}, status=400)
    
    # Process webhook
    payload = json.loads(body)
    event_type = payload['event']['type']
    charge_id = payload['event']['data']['id']
    
    try:
        payment = CryptoPayment.objects.get(charge_id=charge_id)
        
        if event_type == 'charge:confirmed':
            payment.status = 'completed'
        elif event_type == 'charge:failed':
            payment.status = 'failed'
        elif event_type == 'charge:delayed':
            payment.status = 'pending'
        elif event_type == 'charge:pending':
            payment.status = 'pending'
        
        payment.save()
        return JsonResponse({'status': 'success'})
        
    except CryptoPayment.DoesNotExist:
        return JsonResponse({'error': 'Payment not found'}, status=404)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_payment_api(request):
    """API endpoint to create a payment programmatically."""
    try:
        amount_usd = Decimal(request.data.get('amount'))
        crypto_type = request.data.get('crypto_type', 'BTC')
        
        if crypto_type not in ['BTC', 'ETH']:
            return Response({'error': 'Invalid crypto type'}, status=400)
        
        crypto_price = get_crypto_price(crypto_type)
        if not crypto_price:
            return Response({'error': 'Error fetching crypto price'}, status=400)
        
        crypto_amount = amount_usd / crypto_price
        
        # Create Coinbase Commerce charge
        headers = {
            'X-CC-Api-Key': settings.COINBASE_API_KEY,
            'X-CC-Version': '2018-03-22',
            'Content-Type': 'application/json',
        }
        
        payload = {
            'name': f'API Payment of ${amount_usd}',
            'description': f'API Payment of ${amount_usd} in {crypto_type}',
            'pricing_type': 'fixed_price',
            'local_price': {
                'amount': str(amount_usd),
                'currency': 'USD'
            },
            'metadata': {
                'user_id': request.user.id
            }
        }
        
        response = requests.post(
            'https://api.commerce.coinbase.com/charges',
            headers=headers,
            json=payload
        )
        charge_data = response.json()
        
        # Create payment record
        payment = Payment.objects.create(
            user=request.user,
            amount_usd=amount_usd,
            crypto_type=crypto_type,
            crypto_amount=crypto_amount,
            charge_id=charge_data['data']['id'],
            status='pending'
        )
        
        return Response({
            'payment_id': payment.id,
            'charge_url': charge_data['data']['hosted_url']
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=400)

def register(request):
    """Handle user registration."""
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {
        'form': form,
        'hide_navbar': True,
        'allow_anonymous': True
    })

@login_required
def create_subscription(request):
    """Handle subscription creation."""
    if request.method == 'POST':
        try:
            plan_name = request.POST.get('plan_name')
            amount_usd = Decimal(request.POST.get('amount'))
            crypto_type = request.POST.get('crypto_type')
            interval = request.POST.get('interval')
            
            # Get current crypto price
            crypto_price = get_crypto_price(crypto_type)
            if not crypto_price:
                return JsonResponse({
                    'error': 'Error fetching crypto price. Please try again.'
                }, status=400)
            
            crypto_amount = amount_usd / crypto_price
            
            # Create Coinbase Commerce charge for first payment
            headers = {
                'X-CC-Api-Key': settings.COINBASE_API_KEY,
                'X-CC-Version': '2018-03-22',
                'Content-Type': 'application/json',
            }
            
            payload = {
                'name': f'{plan_name} Subscription - ${amount_usd}/{interval}',
                'description': f'Initial payment for {plan_name} subscription',
                'pricing_type': 'fixed_price',
                'local_price': {
                    'amount': str(amount_usd),
                    'currency': 'USD'
                },
                'metadata': {
                    'user_id': request.user.id,
                    'is_subscription': True,
                    'interval': interval
                }
            }
            
            try:
                response = requests.post(
                    'https://api.commerce.coinbase.com/charges',
                    headers=headers,
                    json=payload
                )
                charge_data = response.json()
                
                # Create subscription
                subscription = Subscription.objects.create(
                    user=request.user,
                    plan_name=plan_name,
                    amount_usd=amount_usd,
                    crypto_type=crypto_type,
                    crypto_amount=crypto_amount,
                    interval=interval,
                    status='active'
                )
                
                # Create initial payment
                payment = Payment.objects.create(
                    user=request.user,
                    amount_usd=amount_usd,
                    crypto_type=crypto_type,
                    crypto_amount=crypto_amount,
                    charge_id=charge_data['data']['id'],
                    status='pending',
                    subscription=subscription
                )
                
                return JsonResponse({
                    'success': True,
                    'redirect_url': charge_data['data']['hosted_url']
                })
                
            except Exception as e:
                return JsonResponse({
                    'error': 'Error creating subscription. Please try again.'
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=400)
    
    return render(request, 'payments/create_subscription.html')

@login_required
def manage_subscriptions(request):
    """Display and manage user's subscriptions."""
    subscriptions = Subscription.objects.filter(user=request.user).order_by('-created_at')
    
    # Calculate subscription metrics
    total_active = subscriptions.filter(status='active').count()
    total_monthly_revenue = sum(
        sub.amount_usd for sub in subscriptions.filter(status='active', interval='monthly')
    )
    total_yearly_revenue = sum(
        sub.amount_usd for sub in subscriptions.filter(status='active', interval='yearly')
    )
    
    context = {
        'subscriptions': subscriptions,
        'total_active': total_active,
        'total_monthly_revenue': total_monthly_revenue,
        'total_yearly_revenue': total_yearly_revenue
    }
    
    return render(request, 'payments/manage_subscriptions.html', context)

@login_required
def cancel_subscription(request, subscription_id):
    """Cancel a subscription."""
    try:
        subscription = Subscription.objects.get(id=subscription_id, user=request.user)
        subscription.status = 'canceled'
        subscription.save()
        return JsonResponse({'success': True})
    except Subscription.DoesNotExist:
        return JsonResponse({'error': 'Subscription not found'}, status=404)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_create_charge(request):
    """Create a new payment charge."""
    try:
        amount_usd = Decimal(request.data.get('amount_usd'))
        crypto_type = request.data.get('crypto_type', 'BTC')
        metadata = request.data.get('metadata', {})

        # Validate crypto type
        if crypto_type not in dict(Payment.CRYPTO_CHOICES):
            return Response({
                'error': f'Invalid crypto_type. Supported types: {", ".join(dict(Payment.CRYPTO_CHOICES).keys())}'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get crypto price and calculate amount
        crypto_price = get_crypto_price(crypto_type)
        if not crypto_price:
            return Response({
                'error': f'Unable to fetch {crypto_type} price'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        crypto_amount = amount_usd / crypto_price

        # Create payment record
        payment = Payment.objects.create(
            user=request.user,
            amount_usd=amount_usd,
            crypto_type=crypto_type,
            crypto_amount=crypto_amount,
            metadata=metadata
        )

        # Create Coinbase Commerce charge
        headers = {
            'X-CC-Api-Key': settings.COINBASE_API_KEY,
            'X-CC-Version': '2018-03-22'
        }
        
        charge_data = {
            'name': f'Payment #{payment.id}',
            'description': f'Payment for {request.user.username}',
            'local_price': {
                'amount': str(amount_usd),
                'currency': 'USD'
            },
            'pricing_type': 'fixed_price',
            'metadata': {
                'payment_id': payment.id,
                **metadata
            }
        }

        response = requests.post(
            'https://api.commerce.coinbase.com/charges',
            headers=headers,
            json=charge_data
        )

        if response.status_code != 201:
            payment.delete()
            return Response({
                'error': 'Failed to create charge'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        charge_data = response.json()['data']
        payment.charge_id = charge_data['id']
        payment.save()

        return Response({
            'payment_id': payment.id,
            'payment_url': charge_data['hosted_url'],
            'expires_at': charge_data['expires_at']
        })

    except (ValueError, TypeError) as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_get_payment_status(request, payment_id):
    """Get the status of a payment."""
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    return Response({
        'payment_id': payment.id,
        'status': payment.status,
        'amount_usd': str(payment.amount_usd),
        'crypto_type': payment.crypto_type,
        'crypto_amount': str(payment.crypto_amount),
        'created_at': payment.created_at.isoformat(),
        'updated_at': payment.updated_at.isoformat(),
        'metadata': payment.metadata
    })

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_create_subscription(request):
    """Create a new subscription."""
    try:
        plan_name = request.data.get('plan_name')
        amount_usd = Decimal(request.data.get('amount_usd'))
        crypto_type = request.data.get('crypto_type', 'BTC')
        interval = request.data.get('interval', 'monthly')

        # Validate inputs
        if not plan_name:
            return Response({
                'error': 'plan_name is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        if interval not in dict(Subscription.INTERVAL_CHOICES):
            return Response({
                'error': f'Invalid interval. Supported intervals: {", ".join(dict(Subscription.INTERVAL_CHOICES).keys())}'
            }, status=status.HTTP_400_BAD_REQUEST)

        if crypto_type not in dict(Payment.CRYPTO_CHOICES):
            return Response({
                'error': f'Invalid crypto_type. Supported types: {", ".join(dict(Payment.CRYPTO_CHOICES).keys())}'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get crypto price and calculate amount
        crypto_price = get_crypto_price(crypto_type)
        if not crypto_price:
            return Response({
                'error': f'Unable to fetch {crypto_type} price'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        crypto_amount = amount_usd / crypto_price

        # Create subscription
        subscription = Subscription.objects.create(
            user=request.user,
            plan_name=plan_name,
            amount_usd=amount_usd,
            crypto_type=crypto_type,
            crypto_amount=crypto_amount,
            interval=interval,
            status='active',
            next_renewal=timezone.now() + timezone.timedelta(days=30 if interval == 'monthly' else 365)
        )

        # Create initial payment
        payment = Payment.objects.create(
            user=request.user,
            amount_usd=amount_usd,
            crypto_type=crypto_type,
            crypto_amount=crypto_amount,
            subscription=subscription
        )

        # Create Coinbase Commerce charge for initial payment
        headers = {
            'X-CC-Api-Key': settings.COINBASE_API_KEY,
            'X-CC-Version': '2018-03-22'
        }
        
        charge_data = {
            'name': f'{plan_name} Subscription',
            'description': f'{interval.title()} subscription for {request.user.username}',
            'local_price': {
                'amount': str(amount_usd),
                'currency': 'USD'
            },
            'pricing_type': 'fixed_price',
            'metadata': {
                'payment_id': payment.id,
                'subscription_id': subscription.id
            }
        }

        response = requests.post(
            'https://api.commerce.coinbase.com/charges',
            headers=headers,
            json=charge_data
        )

        if response.status_code != 201:
            subscription.delete()
            payment.delete()
            return Response({
                'error': 'Failed to create charge'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        charge_data = response.json()['data']
        payment.charge_id = charge_data['id']
        payment.save()

        return Response({
            'subscription_id': subscription.id,
            'payment_id': payment.id,
            'payment_url': charge_data['hosted_url'],
            'expires_at': charge_data['expires_at'],
            'next_renewal': subscription.next_renewal.isoformat()
        })

    except (ValueError, TypeError) as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_get_subscription(request, subscription_id):
    """Get subscription details."""
    subscription = get_object_or_404(Subscription, id=subscription_id, user=request.user)
    
    # Get recent payments
    recent_payments = Payment.objects.filter(
        subscription=subscription
    ).order_by('-created_at')[:5]

    return Response({
        'subscription_id': subscription.id,
        'plan_name': subscription.plan_name,
        'amount_usd': str(subscription.amount_usd),
        'crypto_type': subscription.crypto_type,
        'crypto_amount': str(subscription.crypto_amount),
        'interval': subscription.interval,
        'status': subscription.status,
        'created_at': subscription.created_at.isoformat(),
        'last_renewed': subscription.last_renewed.isoformat(),
        'next_renewal': subscription.next_renewal.isoformat(),
        'recent_payments': [{
            'payment_id': payment.id,
            'status': payment.status,
            'created_at': payment.created_at.isoformat()
        } for payment in recent_payments]
    })

@login_required
def manage_api_keys(request):
    """View for managing API keys."""
    if request.method == 'POST':
        action = request.POST.get('action')
        key_id = request.POST.get('key_id')
        
        if action == 'create':
            name = request.POST.get('name', 'My API Key')
            test_mode = request.POST.get('test_mode') == 'true'
            api_key = APIKey.objects.create(
                user=request.user,
                name=name,
                test_mode=test_mode
            )
            return JsonResponse({
                'success': True,
                'key': api_key.key,
                'id': api_key.id,
                'name': api_key.name,
                'test_mode': api_key.test_mode,
                'created_at': api_key.created_at.isoformat()
            })
            
        elif action in ['deactivate', 'reactivate']:
            api_key = get_object_or_404(APIKey, id=key_id, user=request.user)
            if action == 'deactivate':
                api_key.deactivate()
            else:
                api_key.reactivate()
            return JsonResponse({'success': True})
            
        return JsonResponse({'error': 'Invalid action'}, status=400)
        
    api_keys = APIKey.objects.filter(user=request.user)
    return render(request, 'payments/manage_api_keys.html', {
        'api_keys': api_keys
    })

@login_required
def connect_wallet(request):
    """
    Render the wallet connection page.
    """
    # Get user's connected wallets
    wallets = UserWallet.objects.filter(user=request.user, is_active=True).order_by('-created_at')
    
    # Serialize wallet data for the template
    serialized_wallets = [
        {
            'id': wallet.id,
            'crypto_type': wallet.crypto_type,
            'wallet_source': wallet.wallet_source,
            'network': wallet.network,
            'wallet_address': wallet.wallet_address,
            'memo': wallet.memo,
            'created_at': wallet.created_at.isoformat()
        }
        for wallet in wallets
    ]
    
    return render(request, 'payments/connect_wallet.html', {
        'wallets': serialized_wallets,
        'crypto_networks': UserWallet.CRYPTO_NETWORK_MAP,
        'platform_networks': UserWallet.PLATFORM_NETWORK_MAP
    })

@login_required
@require_http_methods(["POST"])
def save_wallet(request):
    """
    Save connected wallet information to the database.
    """
    try:
        data = json.loads(request.body)
        wallet_address = data.get('address')
        wallet_type = data.get('wallet_type')  # This is wallet_source in our model
        network = data.get('network')
        crypto_type = data.get('crypto_type')  # Added crypto_type field
        memo = data.get('memo')  # Optional memo field

        # Validate the data
        if not all([wallet_address, wallet_type, network, crypto_type]):
            return JsonResponse({
                'success': False,
                'error': 'Missing required fields'
            })

        # Check if wallet already exists
        existing_wallet = UserWallet.objects.filter(
            user=request.user,
            wallet_address=wallet_address,
            crypto_type=crypto_type
        ).first()

        try:
            if existing_wallet:
                existing_wallet.network = network
                existing_wallet.wallet_source = wallet_type
                existing_wallet.memo = memo
                existing_wallet.is_active = True
                existing_wallet.save()
            else:
                UserWallet.objects.create(
                    user=request.user,
                    wallet_address=wallet_address,
                    wallet_source=wallet_type,
                    network=network,
                    crypto_type=crypto_type,
                    memo=memo,
                    is_active=True
                )

            return JsonResponse({
                'success': True,
                'message': 'Wallet connected successfully'
            })

        except ValidationError as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
@require_http_methods(["GET"])
def get_connected_wallets(request):
    """
    Get user's connected wallets.
    """
    wallets = UserWallet.objects.filter(user=request.user, is_active=True).order_by('-created_at')
    
    wallet_list = [
        {
            'id': wallet.id,
            'crypto_type': wallet.crypto_type,
            'wallet_source': wallet.wallet_source,
            'network': wallet.network,
            'wallet_address': wallet.wallet_address,
            'memo': wallet.memo,
            'created_at': wallet.created_at.isoformat()
        }
        for wallet in wallets
    ]
    
    return JsonResponse({
        'success': True,
        'wallets': wallet_list
    })

@login_required
@require_http_methods(["POST"])
def delete_wallet(request, wallet_id):
    try:
        wallet = UserWallet.objects.get(id=wallet_id, user=request.user)
        wallet.delete()  # Actually delete the wallet from database
        return JsonResponse({
            'success': True,
            'message': 'Wallet deleted successfully'
        })
    except UserWallet.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Wallet not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_history(request):
    payments = CryptoPayment.objects.filter(user=request.user).order_by('-created_at')
    data = [{
        'id': payment.id,
        'amount_usd': payment.amount_usd,
        'crypto_amount': payment.crypto_amount,
        'crypto_type': payment.crypto_type,
        'status': payment.status,
        'created_at': payment.created_at
    } for payment in payments]
    return Response(data)

def support(request):
    """Display the support page with contact information and FAQs."""
    return render(request, 'payments/support.html', {
        'title': 'Support - CoinFuse',
        'section': 'support'
    })

@login_required
def transaction_history(request):
    """
    Display the transaction history page with a list of all payments.
    """
    return render(request, 'payments/transaction_history.html', {
        'page_title': 'Transaction History',
        'active_tab': 'transactions'
    })

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_transactions(request):
    """
    API endpoint to fetch user's transaction history
    """
    transactions = Payment.objects.filter(user=request.user).order_by('-created_at')
    transactions_list = []
    
    for transaction in transactions:
        transactions_list.append({
            'id': transaction.id,
            'created_at': transaction.created_at.isoformat(),
            'amount_usd': float(transaction.amount_usd),
            'crypto_type': transaction.crypto_type,
            'crypto_amount': float(transaction.crypto_amount),
            'status': transaction.status,
            'charge_id': transaction.charge_id
        })
    
    return Response(transactions_list)
