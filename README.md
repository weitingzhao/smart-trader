# Smart Trader

A comprehensive Django-based platform for stock research, analysis, and automated trading. Smart Trader provides a complete ecosystem for traders and investors to manage portfolios, analyze market data, and execute trading strategies.

## 🎯 Project Overview

Smart Trader is a sophisticated trading platform that combines real-time market data, technical analysis, portfolio management, and automated trading capabilities. The platform is designed for both individual traders and institutional users who need advanced tools for market research and strategy execution.

## ✨ Key Features

### 📊 Market Data & Analysis
- **Real-time Stock Data**: Integration with Yahoo Finance API for live market data
- **Historical Data Management**: TimescaleDB-powered time-series storage for OHLCV data
- **Technical Indicators**: Comprehensive technical analysis tools including:
  - Bollinger Bands with custom smoothing
  - MACD (Moving Average Convergence Divergence)
  - RSI (Relative Strength Index)
  - ADX (Average Directional Index)
  - Custom Nadaraya-Watson smoothing indicators
- **Fundamental Analysis**: Company financials, earnings data, and valuation metrics

### 🔍 Stock Screening & Research
- **Advanced Screeners**: Multi-criteria stock filtering based on technical and fundamental metrics
- **Snapshot System**: Time-series snapshots of market data for historical analysis
- **Research Tools**: Comprehensive research capabilities with customizable indicators
- **Market Comparison**: Side-by-side analysis of multiple securities

### 💼 Portfolio Management
- **Multi-Portfolio Support**: Manage multiple portfolios with different strategies
- **Position Tracking**: Real-time position monitoring and P&L tracking
- **Order Management**: Comprehensive order system with various order types (Market, Limit, Stop, Stop-Limit)
- **Transaction History**: Complete audit trail of all trading activities
- **Cash Flow Management**: Track deposits, withdrawals, and cash balances

### 🤖 Automated Trading
- **Strategy Engine**: Backtrader-based strategy development and backtesting
- **Live Trading**: Real-time strategy execution with Interactive Brokers integration
- **Risk Management**: Built-in risk controls and position sizing
- **Performance Analytics**: Detailed performance metrics and trade analysis

### 📈 Visualization & Reporting
- **Interactive Charts**: Bokeh-powered interactive charts and dashboards
- **Real-time Dashboards**: Live market data visualization
- **Performance Reports**: Comprehensive performance analytics and reporting
- **Custom Indicators**: Support for custom technical indicators and overlays

## 🏗️ Technical Architecture

### Backend Technologies
- **Django 5.1.6**: Web framework with REST API capabilities
- **PostgreSQL + TimescaleDB**: Primary database with time-series optimization
- **Redis**: Caching and message broker for real-time features
- **Celery**: Asynchronous task processing for data fetching and analysis

### Trading & Analysis
- **Backtrader**: Professional backtesting and live trading framework
- **Interactive Brokers API**: Live trading integration
- **yfinance**: Market data provider
- **TA-Lib**: Technical analysis library
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing

### Frontend & Visualization
- **Bootstrap 5**: Responsive UI framework
- **Bokeh**: Interactive data visualization
- **Panel**: Dashboard and app framework
- **WebSockets**: Real-time data streaming

### Data Processing
- **Ray**: Distributed computing for strategy optimization
- **Scikit-learn**: Machine learning capabilities
- **Matplotlib/Plotly**: Additional visualization options

## 📁 Project Structure

```
smart-trader/
├── apps/                    # Django applications
│   ├── api/                # REST API endpoints
│   ├── common/             # Core models and utilities
│   ├── notifications/      # User notification system
│   ├── tasks/              # Celery task management
│   └── file_manager/       # File management utilities
├── business/               # Business logic layer
│   ├── engines/            # Data processing engines
│   ├── services/           # Business services
│   └── research/          # Research and analysis tools
├── cerebro/                # Trading strategy framework
│   ├── strategy/           # Custom trading strategies
│   └── datafeed_tradingview/ # TradingView data integration
├── backtrader/             # Backtrader framework integration
├── home/                   # Main application views
└── templates/              # Django templates
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- PostgreSQL with TimescaleDB extension
- Redis server
- Node.js (for frontend assets)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd smart-trader
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Set up the database**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. **Start the development server**
   ```bash
   python manage.py runserver
   ```

### Configuration

Key environment variables to configure:
- `DB_ENGINE`: Database engine (postgresql)
- `DB_NAME`: Database name
- `DB_USERNAME`: Database username
- `DB_PASS`: Database password
- `REDIS_HOST`: Redis server host
- `SECRET_KEY`: Django secret key
- `TW_USERNAME`: TradingView username (optional)
- `TW_PASSWORD`: TradingView password (optional)

## 🔧 Development Status

This project is actively under development with the following implementation status:

### ✅ Completed Features
- Core Django application structure
- Market data models and APIs
- Portfolio management system
- Basic trading strategy framework
- Data visualization with Bokeh
- User authentication and management

### 🚧 In Development
- Live trading integration
- Advanced strategy optimization
- Real-time data streaming
- Mobile-responsive UI improvements
- Enhanced risk management tools

### 📋 Planned Features
- Machine learning-based strategies
- Social trading features
- Advanced reporting and analytics
- Mobile application
- API marketplace for custom indicators

## 🤝 Contributing

This project welcomes contributions! Please see the contributing guidelines for details on how to:
- Report bugs
- Suggest new features
- Submit pull requests
- Set up the development environment

## 📄 License

This project is licensed under the terms specified in the LICENSE.md file.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the code examples in the `examples/` directory

---

**Note**: This platform is designed for educational and research purposes. Always ensure compliance with local financial regulations when using automated trading features.