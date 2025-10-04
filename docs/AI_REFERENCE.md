# Smart Trader - AI Reference Documentation

## Project Overview

**Smart Trader** is a comprehensive Django-based trading platform that provides a complete ecosystem for stock research, analysis, and automated trading. The platform combines real-time market data, technical analysis, portfolio management, and automated trading capabilities.

## Quick Facts

- **Framework**: Django 5.1.6 with PostgreSQL + TimescaleDB
- **Database**: PostgreSQL with TimescaleDB extension for time-series data
- **Trading Engine**: Backtrader framework with Interactive Brokers integration
- **Data Sources**: Yahoo Finance API, TradingView
- **Frontend**: Bootstrap 5, Bokeh for visualization
- **Task Processing**: Celery with Redis
- **Deployment**: Docker containers with Nginx

## Database Connection Details

### Local Development
```bash
DB_ENGINE=timescale.db.backends.postgresql
DB_NAME=smart_trader
DB_USERNAME=postgres
DB_PASS=Spm123!@#
DB_HOST=10.0.0.80
DB_PORT=5432
```

### Production
```bash
DB_ENGINE=timescale.db.backends.postgresql
DB_NAME=smart_trader
DB_USERNAME=db_connector
DB_PASS=AVNS_jdR9rzh55oyMECoEVkH
DB_HOST=db-postgresql-nyc3-vision-db-001-do-user-18232874-0.f.db.ondigitalocean.com
DB_PORT=25060
```

## Core Database Tables

### Market Data Tables
- **`market_symbol`**: Master table for all market symbols
- **`market_stock`**: Detailed company information
- **`market_stock_hist_bars_min_ts`**: Minute-level price data (TimescaleDB)
- **`market_stock_hist_bars_day_ts`**: Daily price data (TimescaleDB)
- **`market_stock_hist_bars_hour_ts`**: Hourly price data (TimescaleDB)

### Portfolio Management
- **`portfolio`**: User portfolios
- **`holding`**: Stock holdings in portfolios
- **`transaction`**: Buy/sell transactions
- **`order`**: Trading orders
- **`trade`**: Trade records
- **`funding`**: Portfolio funding records
- **`cash_balance`**: Cash balance tracking

### Strategy & Analysis
- **`strategy`**: Trading strategies
- **`screening`**: Stock screening configurations
- **`wishlist`**: Stock watchlist from screening
- **`rating`**: Strategy ratings for symbols
- **`rating_indicator_result`**: Technical indicator results

### Snapshot Tables (TimescaleDB)
- **`snapshot_screening`**: Screening result snapshots
- **`snapshot_overview`**: Overview snapshots
- **`snapshot_technical`**: Technical analysis snapshots
- **`snapshot_fundamental`**: Fundamental analysis snapshots
- **`snapshot_bull_flag`**: Bull flag pattern snapshots
- **`snapshot_earning`**: Earnings snapshots

## Key Django Models

### Market Models (`apps/common/models/market.py`)
```python
class MarketSymbol(models.Model):
    symbol = models.CharField(max_length=20, unique=True, primary_key=True)
    name = models.CharField(max_length=200)
    market = models.CharField(max_length=50)
    asset_type = models.CharField(max_length=50)
    # ... other fields

class MarketStockHistoricalBarsByMin(TimescaleModel):
    symbol = models.CharField(max_length=10)
    time = models.DateTimeField()  # TimescaleDB timestamp
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    volume = models.FloatField()
    # ... other fields
```

### Portfolio Models (`apps/common/models/portfolio.py`)
```python
class Portfolio(models.Model):
    portfolio_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    money_market = models.DecimalField(max_digits=15, decimal_places=2)
    cash = models.DecimalField(max_digits=15, decimal_places=2)
    investment = models.DecimalField(max_digits=15, decimal_places=2)
    # ... other fields

class Holding(models.Model):
    holding_id = models.AutoField(primary_key=True)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    symbol = models.ForeignKey(MarketSymbol, on_delete=models.DO_NOTHING)
```

### Snapshot Models (`apps/common/models/snapshot.py`)
```python
class Snapshot(TimescaleModel):
    symbol = models.ForeignKey(MarketSymbol, on_delete=models.DO_NOTHING)
    time = models.DateField()
    class Meta:
        abstract = True

class SnapshotTechnical(Snapshot):
    lower_bollinger_band = models.DecimalField(max_digits=20, decimal_places=2)
    upper_bollinger_band = models.DecimalField(max_digits=20, decimal_places=2)
    RSI_14 = models.DecimalField(max_digits=20, decimal_places=2)
    MACD_12_26_9 = models.DecimalField(max_digits=20, decimal_places=2)
    # ... other technical indicators
```

## Business Logic Architecture

### Data Processing Engines (`business/engines/`)
- **`WebEngine`**: Web data fetching
- **`PgSqlEngine`**: PostgreSQL operations
- **`SqlAlchemyEngine`**: SQLAlchemy operations
- **`JsonEngine`**: JSON data handling
- **`CsvEngine`**: CSV data processing
- **`NotifyEngine`**: Notification system

### Services (`business/services/`)
- **`FetchingService`**: Data fetching operations
- **`LoadingService`**: Data loading operations
- **`SavingService`**: Data saving operations

### Trading Strategy Framework (`cerebro/`)
- **`cerebro_base.py`**: Base trading framework
- **`strategy/`**: Custom trading strategies
- **`datafeed_tradingview/`**: TradingView data integration

## Key Features

### 1. Market Data Management
- Real-time data from Yahoo Finance API
- Historical data storage in TimescaleDB
- Multiple timeframes (minute, hour, daily)
- Automatic data synchronization

### 2. Portfolio Management
- Multi-portfolio support per user
- Real-time position tracking
- Order management system
- Transaction history and audit trail
- Cash flow management

### 3. Trading Strategies
- Backtrader-based strategy development
- Backtesting capabilities
- Live trading with Interactive Brokers
- Custom technical indicators
- Risk management tools

### 4. Stock Screening
- Multi-criteria stock filtering
- Technical and fundamental analysis
- Automated screening operations
- Wishlist management
- Snapshot system for historical analysis

### 5. Data Visualization
- Interactive Bokeh charts
- Real-time dashboards
- Performance analytics
- Custom indicator overlays

## API Endpoints

### REST API (`apps/api/`)
- Market data endpoints
- Portfolio management endpoints
- Strategy endpoints
- User management endpoints

### WebSocket Support
- Real-time data streaming
- Live trading updates
- Notification system

## Task Processing

### Celery Tasks (`apps/tasks/`)
- **Data Fetching**: Automated market data collection
- **Screening Operations**: Automated stock screening
- **Strategy Execution**: Automated trading
- **Notification Tasks**: User notifications

### Task Queues
- `fetching_queue`: Data fetching tasks
- `screening_queue`: Screening operations
- `trading_queue`: Trading operations

## Configuration Files

### Environment Variables
- `.env`: Local development configuration
- `.env.docker`: Docker container configuration

### Django Settings (`core/settings.py`)
- Database configuration
- Celery configuration
- Redis configuration
- API settings
- Authentication settings

## Docker Configuration

### Services
- **smart-trader**: Main Django application
- **celery**: Task processing worker
- **nginx**: Web server and reverse proxy
- **redis**: Message broker and cache
- **postgres**: Database server (TimescaleDB)

### Docker Compose Files
- `docker-compose.yml`: Main application services
- `docker-compose-db.yml`: Database service

## Development Workflow

### Data Flow
1. **Market Data Ingestion**: Yahoo Finance API → TimescaleDB
2. **Screening Process**: Screening configs → Wishlist → Orders
3. **Portfolio Management**: Orders → Transactions → Holdings
4. **Analysis**: Historical data → Snapshots → Ratings
5. **Trading**: Orders → Interactive Brokers → Updates

### Key Commands
```bash
# Start development server
python manage.py runserver

# Run Celery worker
celery -A apps.tasks worker -l info

# Database migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

## Security Considerations

- Database credentials in environment variables
- User authentication through Django's auth system
- Row-level security for user-specific data
- Encrypted connections for production database
- CSRF protection enabled
- Secure session management

## Performance Optimization

- TimescaleDB compression for historical data
- Database indexing for time-series queries
- Redis caching for frequently accessed data
- Celery for asynchronous task processing
- Database connection pooling

## Monitoring and Logging

- Celery task monitoring
- Database performance monitoring
- Application logging
- Error tracking and reporting

## Common Queries for AI

### Get Market Data
```python
# Get latest price for a symbol
from apps.common.models import MarketStockHistoricalBarsByDay
latest_price = MarketStockHistoricalBarsByDay.objects.filter(
    symbol='AAPL'
).latest('time')

# Get historical data for a symbol
historical_data = MarketStockHistoricalBarsByDay.objects.filter(
    symbol='AAPL',
    time__gte='2024-01-01'
).order_by('time')
```

### Portfolio Operations
```python
# Get user's portfolio
from apps.common.models import Portfolio
portfolio = Portfolio.objects.filter(user=request.user, is_default=True).first()

# Get portfolio holdings
holdings = portfolio.holding_set.all()

# Get recent transactions
from apps.common.models import Transaction
recent_transactions = Transaction.objects.filter(
    holding__portfolio=portfolio
).order_by('-date')[:10]
```

### Strategy Operations
```python
# Get active strategies
from apps.common.models import Strategy
active_strategies = Strategy.objects.filter(
    owner_user=request.user
).order_by('custom_order')

# Get strategy ratings
from apps.common.models import Rating
ratings = Rating.objects.filter(
    strategy=strategy,
    time__gte='2024-01-01'
).order_by('-time')
```

## Troubleshooting

### Common Issues
1. **Database Connection**: Check environment variables and network connectivity
2. **Celery Tasks**: Ensure Redis is running and workers are active
3. **Data Fetching**: Check Yahoo Finance API limits and symbol validity
4. **TimescaleDB**: Verify TimescaleDB extension is installed

### Debug Commands
```bash
# Check database connection
python manage.py dbshell

# Check Celery status
celery -A apps.tasks inspect active

# Check Redis connection
redis-cli ping
```

---

*This documentation serves as a comprehensive reference for AI systems working with the Smart Trader project. It should be updated when significant changes are made to the codebase.*
