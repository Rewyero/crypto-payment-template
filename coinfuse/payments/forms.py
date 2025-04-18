from django import forms
from .models import UserWallet, Payment, Subscription

class WalletForm(forms.ModelForm):
    class Meta:
        model = UserWallet
        fields = ['crypto_type', 'wallet_source', 'network', 'wallet_address', 'memo']
        widgets = {
            'crypto_type': forms.Select(attrs={
                'class': 'mt-1 block w-full bg-[#1E293B] border border-gray-600 rounded-lg shadow-sm py-2 px-3 text-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'wallet_source': forms.Select(attrs={
                'class': 'mt-1 block w-full bg-[#1E293B] border border-gray-600 rounded-lg shadow-sm py-2 px-3 text-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'network': forms.Select(attrs={
                'class': 'mt-1 block w-full bg-[#1E293B] border border-gray-600 rounded-lg shadow-sm py-2 px-3 text-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'wallet_address': forms.TextInput(attrs={
                'class': 'mt-1 block w-full bg-[#1E293B] border border-gray-600 rounded-lg shadow-sm py-2 px-3 text-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-mono',
                'placeholder': 'Enter wallet address'
            }),
            'memo': forms.TextInput(attrs={
                'class': 'mt-1 block w-full bg-[#1E293B] border border-gray-600 rounded-lg shadow-sm py-2 px-3 text-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-mono',
                'placeholder': 'Optional: Enter memo/tag'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['memo'].required = False
        
        # Add choices from model
        self.fields['crypto_type'].choices = UserWallet.CRYPTO_CHOICES
        self.fields['wallet_source'].choices = UserWallet.WALLET_SOURCE_CHOICES
        self.fields['network'].choices = UserWallet.NETWORK_CHOICES

    def clean(self):
        cleaned_data = super().clean()
        crypto_type = cleaned_data.get('crypto_type')
        network = cleaned_data.get('network')
        wallet_source = cleaned_data.get('wallet_source')
        wallet_address = cleaned_data.get('wallet_address')

        # Validate network compatibility with crypto type
        if crypto_type and network:
            valid_networks = UserWallet.CRYPTO_NETWORK_MAP.get(crypto_type, [])
            if network not in valid_networks:
                raise forms.ValidationError({
                    'network': f'Selected network is not compatible with {crypto_type}'
                })

        # Validate platform-specific network compatibility
        if wallet_source in ['Revolut', 'Bybit']:
            platform_networks = UserWallet.PLATFORM_NETWORK_MAP[wallet_source].get(crypto_type, [])
            if network not in platform_networks:
                raise forms.ValidationError({
                    'network': f'{wallet_source} does not support {crypto_type} on {network}'
                })

        # For testing purposes, we'll skip wallet address format validation in the form
        # In production, you should add proper validation here

        return cleaned_data 

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount_usd', 'crypto_type', 'crypto_amount', 'wallet_address']
        widgets = {
            'amount_usd': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full bg-[#1E293B] border border-gray-600 rounded-lg shadow-sm py-2 px-3 text-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Enter amount in USD',
                'step': '0.01'
            }),
            'crypto_type': forms.Select(attrs={
                'class': 'mt-1 block w-full bg-[#1E293B] border border-gray-600 rounded-lg shadow-sm py-2 px-3 text-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'crypto_amount': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full bg-[#1E293B] border border-gray-600 rounded-lg shadow-sm py-2 px-3 text-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Crypto amount will be calculated',
                'readonly': True
            }),
            'wallet_address': forms.TextInput(attrs={
                'class': 'mt-1 block w-full bg-[#1E293B] border border-gray-600 rounded-lg shadow-sm py-2 px-3 text-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-mono',
                'placeholder': 'Enter wallet address'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['crypto_type'].choices = Payment.CRYPTO_CHOICES
        self.fields['crypto_amount'].required = False  # Will be calculated automatically

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['plan_name', 'amount_usd', 'crypto_type', 'crypto_amount', 'interval']
        widgets = {
            'plan_name': forms.TextInput(attrs={
                'class': 'mt-1 block w-full bg-[#1E293B] border border-gray-600 rounded-lg shadow-sm py-2 px-3 text-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Enter plan name'
            }),
            'amount_usd': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full bg-[#1E293B] border border-gray-600 rounded-lg shadow-sm py-2 px-3 text-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Enter amount in USD',
                'step': '0.01'
            }),
            'crypto_type': forms.Select(attrs={
                'class': 'mt-1 block w-full bg-[#1E293B] border border-gray-600 rounded-lg shadow-sm py-2 px-3 text-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            }),
            'crypto_amount': forms.NumberInput(attrs={
                'class': 'mt-1 block w-full bg-[#1E293B] border border-gray-600 rounded-lg shadow-sm py-2 px-3 text-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
                'placeholder': 'Crypto amount will be calculated',
                'readonly': True
            }),
            'interval': forms.Select(attrs={
                'class': 'mt-1 block w-full bg-[#1E293B] border border-gray-600 rounded-lg shadow-sm py-2 px-3 text-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['crypto_type'].choices = Subscription.CRYPTO_CHOICES
        self.fields['interval'].choices = Subscription.INTERVAL_CHOICES
        self.fields['crypto_amount'].required = False  # Will be calculated automatically 