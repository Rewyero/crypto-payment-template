# CoinFuse - Modern Crypto Payment Processing Platform

![CoinFuse Banner](docs/banner.png)

CoinFuse is a modern, Stripe-like cryptocurrency payment processing platform built with Django and Tailwind CSS. It provides businesses with a seamless way to accept and manage cryptocurrency payments with a beautiful, user-friendly interface.

## ✨ Features

- 🎨 Modern, responsive UI with Tailwind CSS and glassmorphism effects
- 💰 Support for multiple cryptocurrencies (BTC, ETH, SOL, etc.)
- 🔒 Secure wallet management system
- 📊 Real-time payment tracking and analytics
- 💳 Easy-to-use payment creation flow
- 🔌 RESTful API with comprehensive documentation
- 📱 Mobile-friendly dashboard
- 🌐 Integration with Coinbase Commerce
- 📈 Real-time crypto price conversions
- 🔐 User authentication and authorization
- 📨 Webhook support for payment notifications

## 🚀 Tech Stack

- **Backend:** Django 5.2
- **Frontend:** Tailwind CSS, Alpine.js
- **Database:** PostgreSQL
- **API Integration:** Coinbase Commerce, CoinGecko
- **Icons:** Font Awesome 6
- **Authentication:** Django Authentication System
- **API Framework:** Django REST Framework

## 📋 Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.12 or higher
- Node.js 18+ and npm
- PostgreSQL 13+
- Git

## ⚙️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/coinfuse.git
   cd coinfuse
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   .\venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Create .env file
   cp .env.example .env
   
   # Update the following variables in .env:
   SECRET_KEY=your_secret_key
   DEBUG=True
   DATABASE_URL=postgresql://user:password@localhost:5432/coinfuse
   COINBASE_API_KEY=your_coinbase_api_key
   COINBASE_WEBHOOK_SECRET=your_webhook_secret
   ```

5. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

Visit `http://127.0.0.1:8000` to access the application.

## 🔧 Configuration

### Coinbase Commerce Setup

1. Create a Coinbase Commerce account at https://commerce.coinbase.com
2. Generate an API key from the Settings → API keys section
3. Add the API key to your `.env` file
4. Configure webhook URL in Coinbase Commerce settings:
   - Webhook URL: `https://your-domain.com/payments/webhook/`
   - Add the webhook secret to your `.env` file

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | None |
| `DEBUG` | Debug mode | False |
| `ALLOWED_HOSTS` | Allowed hosts | [] |
| `DATABASE_URL` | Database connection URL | None |
| `COINBASE_API_KEY` | Coinbase Commerce API key | None |
| `COINBASE_WEBHOOK_SECRET` | Coinbase Commerce webhook secret | None |

## 📚 API Documentation

API documentation is available at `/docs/api-reference/` when running the server. The API supports:

- Payment creation and management
- Wallet operations
- Transaction history
- Subscription management
- Webhook handling

## 🎨 Customization

### Tailwind Configuration

The project uses Tailwind CSS with custom configuration. To modify the theme:

1. Edit `tailwind.config.js`
2. Update color schemes in `theme.extend.colors`
3. Run `npm run build` to rebuild CSS

### Adding New Cryptocurrencies

1. Update `CRYPTO_CHOICES` in `payments/models.py`
2. Add necessary icons and colors in templates
3. Update price fetching logic in `payments/utils.py`

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Tailwind CSS](https://tailwindcss.com)
- [Django](https://www.djangoproject.com)
- [Coinbase Commerce](https://commerce.coinbase.com)
- [Font Awesome](https://fontawesome.com)
- [Alpine.js](https://alpinejs.dev)

## 📧 Support

For support, email support@coinfuse.com or open an issue in the GitHub repository.

## 🔮 Roadmap

- [ ] Multi-currency support
- [ ] Advanced analytics dashboard
- [ ] Mobile app
- [ ] Payment link generation
- [ ] Enhanced subscription management
- [ ] Multi-vendor support
- [ ] Enhanced security features
- [ ] More payment gateways

---

Made with ❤️ by ME :)
