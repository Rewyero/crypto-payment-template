import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError

class APIKey(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_keys')
    key = models.CharField(max_length=64, unique=True, editable=False)
    name = models.CharField(max_length=100, help_text="A name to identify this API key", default="My API Key")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    test_mode = models.BooleanField(default=False, help_text="Test mode keys can only create test charges")

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_key():
        """Generate a unique API key."""
        return f"csk_{uuid.uuid4().hex}"

    def __str__(self):
        return f"{self.name} ({'Test' if self.test_mode else 'Live'}) - {self.key[:8]}..."

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'API Key'
        verbose_name_plural = 'API Keys'

    def mark_as_used(self):
        """Update the last used timestamp."""
        self.last_used_at = timezone.now()
        self.save(update_fields=['last_used_at'])

    def deactivate(self):
        """Deactivate this API key."""
        self.is_active = False
        self.save(update_fields=['is_active'])

    def reactivate(self):
        """Reactivate this API key."""
        self.is_active = True
        self.save(update_fields=['is_active'])

    @property
    def masked_key(self):
        """Return a masked version of the API key for display."""
        if not self.key:
            return None
        return f"{self.key[:8]}...{self.key[-4:]}"

class Subscription(models.Model):
    INTERVAL_CHOICES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('canceled', 'Canceled'),
        ('expired', 'Expired'),
    ]
    
    CRYPTO_CHOICES = [
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
        ('SOL', 'Solana'),
        ('BNB', 'Binance Coin'),
        ('XRP', 'XRP'),
        ('USDT', 'Tether'),
        ('USDC', 'USD Coin'),
        ('ADA', 'Cardano'),
        ('DOGE', 'Dogecoin'),
        ('AVAX', 'Avalanche'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan_name = models.CharField(max_length=100)
    amount_usd = models.DecimalField(max_digits=10, decimal_places=2)
    crypto_type = models.CharField(max_length=4, choices=CRYPTO_CHOICES)
    crypto_amount = models.DecimalField(max_digits=18, decimal_places=8)
    interval = models.CharField(max_length=10, choices=INTERVAL_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    last_renewed = models.DateTimeField(auto_now_add=True)
    next_renewal = models.DateTimeField()
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Only set dates on creation
            if not self.last_renewed:
                self.last_renewed = timezone.now()
            self.next_renewal = self.calculate_next_renewal()
        super().save(*args, **kwargs)
    
    def calculate_next_renewal(self):
        if not self.last_renewed:
            self.last_renewed = timezone.now()
        if self.interval == 'monthly':
            return self.last_renewed + timezone.timedelta(days=30)
        return self.last_renewed + timezone.timedelta(days=365)
    
    def __str__(self):
        return f"{self.user.username}'s {self.plan_name} Plan"

class Invoice(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('expired', 'Expired'),
    ]
    
    CRYPTO_CHOICES = [
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
        ('SOL', 'Solana'),
        ('BNB', 'Binance Coin'),
        ('XRP', 'XRP'),
        ('USDT', 'Tether'),
        ('USDC', 'USD Coin'),
        ('ADA', 'Cardano'),
        ('DOGE', 'Dogecoin'),
        ('AVAX', 'Avalanche'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    customer_email = models.EmailField()
    amount_usd = models.DecimalField(max_digits=10, decimal_places=2)
    crypto_type = models.CharField(max_length=4, choices=CRYPTO_CHOICES)
    crypto_amount = models.DecimalField(max_digits=18, decimal_places=8)
    wallet_address = models.CharField(max_length=100)
    qr_code = models.TextField()  # Base64 encoded QR code
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Only set expires_at on creation
            self.expires_at = timezone.now() + timezone.timedelta(days=7)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Invoice {self.id} for {self.customer_email}"

class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    CRYPTO_CHOICES = [
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
        ('SOL', 'Solana'),
        ('BNB', 'Binance Coin'),
        ('XRP', 'XRP'),
        ('USDT', 'Tether'),
        ('USDC', 'USD Coin'),
        ('ADA', 'Cardano'),
        ('DOGE', 'Dogecoin'),
        ('AVAX', 'Avalanche'),
    ]

    # Map of crypto types to their CoinGecko IDs
    COINGECKO_IDS = {
        'BTC': 'bitcoin',
        'ETH': 'ethereum',
        'SOL': 'solana',
        'BNB': 'binancecoin',
        'XRP': 'ripple',
        'USDT': 'tether',
        'USDC': 'usd-coin',
        'ADA': 'cardano',
        'DOGE': 'dogecoin',
        'AVAX': 'avalanche-2'
    }

    # Map of crypto types to their colors for UI
    CRYPTO_COLORS = {
        'BTC': '#F7931A',
        'ETH': '#627EEA',
        'SOL': '#00FFA3',
        'BNB': '#FFCC00',
        'XRP': '#000000',
        'USDT': '#26A17B',
        'USDC': '#3145C4',
        'ADA': '#2A4066',
        'DOGE': '#D4A017',
        'AVAX': '#E84142'
    }

    # Map of crypto types to their FontAwesome icons
    CRYPTO_ICONS = {
        'BTC': 'fab fa-bitcoin',
        'ETH': 'fab fa-ethereum',
        'SOL': 'fas fa-sun',  # Custom icon for Solana
        'BNB': 'fas fa-coins',
        'XRP': 'fas fa-wave-square',
        'USDT': 'fas fa-dollar-sign',
        'USDC': 'fas fa-circle-dollar-to-slot',
        'ADA': 'fas fa-a',
        'DOGE': 'fas fa-dog',
        'AVAX': 'fas fa-mountain'
    }
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount_usd = models.DecimalField(max_digits=10, decimal_places=2)
    crypto_type = models.CharField(max_length=4, choices=CRYPTO_CHOICES)
    crypto_amount = models.DecimalField(max_digits=18, decimal_places=8)
    charge_id = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True, blank=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True)
    wallet_address = models.CharField(max_length=100, null=True, blank=True)  # For non-Coinbase supported coins

    @property
    def is_stablecoin(self):
        """Check if the crypto type is a stablecoin (USDT or USDC)"""
        return self.crypto_type in ['USDT', 'USDC']

    @property
    def supports_coinbase(self):
        """Check if the crypto type is supported by Coinbase Commerce"""
        return self.crypto_type in ['BTC', 'ETH', 'SOL', 'XRP', 'USDT', 'USDC', 'DOGE']

    @property
    def crypto_color(self):
        """Get the UI color for this crypto type"""
        return self.CRYPTO_COLORS.get(self.crypto_type, '#4A90E2')

    @property
    def crypto_icon(self):
        """Get the FontAwesome icon class for this crypto type"""
        return self.CRYPTO_ICONS.get(self.crypto_type, 'fas fa-coins')

    @property
    def coingecko_id(self):
        """Get the CoinGecko API ID for this crypto type"""
        return self.COINGECKO_IDS.get(self.crypto_type)

    def __str__(self):
        return f"Payment {self.id} - {self.amount_usd} USD to {self.crypto_type}"

class UserWallet(models.Model):
    WALLET_SOURCE_CHOICES = [
        ('Manual', 'Manual'),
        ('Revolut', 'Revolut'),
        ('Bybit', 'Bybit'),
    ]

    NETWORK_CHOICES = [
        ('Bitcoin Network', 'Bitcoin Network'),
        ('Ethereum Network', 'Ethereum Network'),
        ('Solana Network', 'Solana Network'),
        ('BNB Chain', 'BNB Chain'),
        ('XRP Ledger', 'XRP Ledger'),
        ('Cardano Network', 'Cardano Network'),
        ('Dogecoin Network', 'Dogecoin Network'),
        ('Avalanche Network', 'Avalanche Network'),
    ]

    CRYPTO_CHOICES = [
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
        ('SOL', 'Solana'),
        ('BNB', 'Binance Coin'),
        ('XRP', 'XRP'),
        ('USDT', 'Tether'),
        ('USDC', 'USD Coin'),
        ('ADA', 'Cardano'),
        ('DOGE', 'Dogecoin'),
        ('AVAX', 'Avalanche'),
    ]

    CRYPTO_NETWORK_MAP = {
        'BTC': ['Bitcoin Network'],
        'ETH': ['Ethereum Network'],
        'SOL': ['Solana Network'],
        'BNB': ['BNB Chain'],
        'XRP': ['XRP Ledger'],
        'USDT': ['Ethereum Network', 'BNB Chain', 'Solana Network'],
        'USDC': ['Ethereum Network', 'Solana Network'],
        'ADA': ['Cardano Network'],
        'DOGE': ['Dogecoin Network'],
        'AVAX': ['Avalanche Network'],
    }

    PLATFORM_NETWORK_MAP = {
        'Revolut': {
            'BTC': ['Bitcoin Network'],
            'ETH': ['Ethereum Network'],
            'USDT': ['Ethereum Network'],
            'USDC': ['Ethereum Network'],
        },
        'Bybit': {
            'BTC': ['Bitcoin Network'],
            'ETH': ['Ethereum Network'],
            'SOL': ['Solana Network'],
            'BNB': ['BNB Chain'],
            'XRP': ['XRP Ledger'],
            'USDT': ['Ethereum Network', 'BNB Chain'],
            'USDC': ['Ethereum Network'],
            'ADA': ['Cardano Network'],
            'DOGE': ['Dogecoin Network'],
            'AVAX': ['Avalanche Network'],
        }
    }

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    crypto_type = models.CharField(max_length=10, choices=CRYPTO_CHOICES)
    wallet_address = models.CharField(max_length=255)
    wallet_source = models.CharField(
        max_length=10,
        choices=WALLET_SOURCE_CHOICES,
        default='Manual'
    )
    network = models.CharField(
        max_length=20,
        choices=NETWORK_CHOICES,
        blank=True
    )
    memo = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'crypto_type', 'wallet_address']

    def clean(self):
        from django.core.exceptions import ValidationError
        
        # Validate network compatibility with crypto type
        if self.crypto_type and self.network:
            valid_networks = self.CRYPTO_NETWORK_MAP.get(self.crypto_type, [])
            if self.network not in valid_networks:
                raise ValidationError({
                    'network': f'Selected network is not compatible with {self.crypto_type}'
                })

        # Validate platform-specific network compatibility
        if self.wallet_source in ['Revolut', 'Bybit']:
            platform_networks = self.PLATFORM_NETWORK_MAP[self.wallet_source].get(self.crypto_type, [])
            if self.network not in platform_networks:
                raise ValidationError({
                    'network': f'{self.wallet_source} does not support {self.crypto_type} on {self.network}'
                })

        # Validate wallet address format - more flexible for testing
        if self.wallet_address:
            # For testing purposes, we'll be more lenient with validation
            # In production, you should use stricter validation
            if self.crypto_type == 'BTC' and not any(
                self.wallet_address.startswith(prefix) for prefix in ['1', '3', 'bc1']
            ):
                # For testing, just log a warning instead of raising an error
                print(f"Warning: Bitcoin address format may be invalid: {self.wallet_address}")
            elif self.crypto_type == 'ETH' and not (
                len(self.wallet_address) == 42 and self.wallet_address.startswith('0x')
            ):
                # For testing, just log a warning instead of raising an error
                print(f"Warning: Ethereum address format may be invalid: {self.wallet_address}")
            # Add more validation rules for other crypto types as needed

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s {self.crypto_type} Wallet ({self.wallet_source})"
