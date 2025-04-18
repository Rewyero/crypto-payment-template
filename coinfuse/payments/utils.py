import requests
from decimal import Decimal
from django.conf import settings

# Mapping of crypto symbols to CoinGecko IDs
COINGECKO_IDS = {
    'BTC': 'bitcoin',
    'ETH': 'ethereum',
    'USDT': 'tether',
    'USDC': 'usd-coin',
    'BNB': 'binancecoin',
    'XRP': 'ripple',
    'ADA': 'cardano',
    'DOGE': 'dogecoin',
    'SOL': 'solana',
    'MATIC': 'matic-network',
}

def get_crypto_price(crypto_symbol):
    """
    Get the current price of a cryptocurrency in USD using CoinGecko API.
    
    Args:
        crypto_symbol (str): The symbol of the cryptocurrency (e.g., 'BTC', 'ETH')
        
    Returns:
        Decimal: The current price in USD, or None if the request fails
    """
    try:
        # Handle stablecoins
        if crypto_symbol in ['USDT', 'USDC']:
            return Decimal('1.0')
            
        # Get CoinGecko ID for the crypto symbol
        crypto_id = COINGECKO_IDS.get(crypto_symbol.upper())
        if not crypto_id:
            return None
            
        # CoinGecko API endpoint
        url = f'https://api.coingecko.com/api/v3/simple/price'
        params = {
            'ids': crypto_id,
            'vs_currencies': 'usd',
            'x_cg_demo_api_key': settings.COINGECKO_API_KEY
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return Decimal(str(data[crypto_id]['usd']))
        return None
    except Exception as e:
        print(f"Error fetching {crypto_symbol} price:", e)
        return None 