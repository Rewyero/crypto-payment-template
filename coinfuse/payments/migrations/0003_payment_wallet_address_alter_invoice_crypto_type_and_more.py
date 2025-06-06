# Generated by Django 5.2 on 2025-04-08 22:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_alter_payment_options_alter_payment_charge_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='wallet_address',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='crypto_type',
            field=models.CharField(choices=[('BTC', 'Bitcoin'), ('ETH', 'Ethereum'), ('SOL', 'Solana'), ('BNB', 'Binance Coin'), ('XRP', 'XRP'), ('USDT', 'Tether'), ('USDC', 'USD Coin'), ('ADA', 'Cardano'), ('DOGE', 'Dogecoin'), ('AVAX', 'Avalanche')], max_length=4),
        ),
        migrations.AlterField(
            model_name='payment',
            name='crypto_type',
            field=models.CharField(choices=[('BTC', 'Bitcoin'), ('ETH', 'Ethereum'), ('SOL', 'Solana'), ('BNB', 'Binance Coin'), ('XRP', 'XRP'), ('USDT', 'Tether'), ('USDC', 'USD Coin'), ('ADA', 'Cardano'), ('DOGE', 'Dogecoin'), ('AVAX', 'Avalanche')], max_length=4),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='crypto_type',
            field=models.CharField(choices=[('BTC', 'Bitcoin'), ('ETH', 'Ethereum'), ('SOL', 'Solana'), ('BNB', 'Binance Coin'), ('XRP', 'XRP'), ('USDT', 'Tether'), ('USDC', 'USD Coin'), ('ADA', 'Cardano'), ('DOGE', 'Dogecoin'), ('AVAX', 'Avalanche')], max_length=4),
        ),
    ]
