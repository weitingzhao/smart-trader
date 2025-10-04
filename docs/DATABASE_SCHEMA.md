# Smart Trader Database Schema Documentation

## Overview

This document provides a comprehensive overview of the Smart Trader database schema. The database is built on **PostgreSQL with TimescaleDB** extension for time-series data optimization, supporting real-time trading data, portfolio management, and strategy execution.

## Database Configuration

- **Engine**: `timescale.db.backends.postgresql`
- **Database**: `smart_trader`
- **Host**: `10.0.0.80` (local) / `db-postgresql-nyc3-vision-db-001-do-user-18232874-0.f.db.ondigitalocean.com` (production)
- **Port**: `5432` (local) / `25060` (production)
- **Username**: `postgres` / `db_connector`
- **TimescaleDB**: Enabled for time-series optimization

## Core Tables

### 1. Market Data Tables

#### `market_symbol`
**Purpose**: Master table for all market symbols (stocks, ETFs, etc.)

| Column | Type | Description |
|--------|------|-------------|
| `symbol` | VARCHAR(20) | Primary key - Stock symbol (e.g., AAPL, MSFT) |
| `name` | VARCHAR(200) | Full company name |
| `market` | VARCHAR(50) | Market exchange (NYSE, NASDAQ, etc.) |
| `asset_type` | VARCHAR(50) | Type of asset (Stock, ETF, etc.) |
| `ipo_date` | DATE | Initial public offering date |
| `delisting_date` | DATE | Delisting date if applicable |
| `status` | VARCHAR(20) | Current status |
| `has_company_info` | BOOLEAN | Whether company info is available |
| `is_delisted` | BOOLEAN | Delisting status |
| `min_period_yfinance` | VARCHAR(20) | Minimum period for yfinance API |
| `daily_period_yfinance` | VARCHAR(20) | Daily period for yfinance API |

#### `market_stock`
**Purpose**: Detailed company information for stocks

| Column | Type | Description |
|--------|------|-------------|
| `symbol` | VARCHAR(20) | Foreign key to market_symbol |
| `underlying_symbol` | VARCHAR(10) | Underlying symbol for derivatives |
| `short_name` | VARCHAR(100) | Short company name |
| `long_name` | VARCHAR(200) | Long company name |
| `address1` | VARCHAR(255) | Company address |
| `city` | VARCHAR(100) | Company city |
| `state` | VARCHAR(50) | Company state |
| `zip` | VARCHAR(20) | ZIP code |
| `country` | VARCHAR(100) | Country |
| `phone` | VARCHAR(20) | Phone number |
| `website` | URL | Company website |
| `industry` | VARCHAR(100) | Industry classification |
| `sector` | VARCHAR(100) | Sector classification |
| `long_business_summary` | TEXT | Business description |
| `full_time_employees` | INTEGER | Employee count |
| `currency` | VARCHAR(10) | Trading currency |
| `financial_currency` | VARCHAR(10) | Financial reporting currency |
| `exchange` | VARCHAR(10) | Trading exchange |
| `quote_type` | VARCHAR(10) | Quote type |
| `time_zone_full_name` | VARCHAR(50) | Full timezone name |
| `time_zone_short_name` | VARCHAR(10) | Short timezone name |
| `gmt_offset_milliseconds` | BIGINT | GMT offset |
| `uuid` | UUID | Unique identifier |

### 2. Time-Series Data Tables (TimescaleDB)

#### `market_stock_hist_bars_min_ts`
**Purpose**: Minute-level historical price data

| Column | Type | Description |
|--------|------|-------------|
| `symbol` | VARCHAR(10) | Stock symbol |
| `time` | TIMESTAMPTZ | Timestamp (TimescaleDB) |
| `open` | FLOAT | Opening price |
| `high` | FLOAT | High price |
| `low` | FLOAT | Low price |
| `close` | FLOAT | Closing price |
| `volume` | FLOAT | Trading volume |
| `dividend` | FLOAT | Dividend amount |
| `stock_splits` | FLOAT | Stock split ratio |

**Constraints**: Unique constraint on (symbol, time)

#### `market_stock_hist_bars_day_ts`
**Purpose**: Daily historical price data

| Column | Type | Description |
|--------|------|-------------|
| `symbol` | VARCHAR(10) | Stock symbol |
| `time` | DATE | Date |
| `open` | FLOAT | Opening price |
| `high` | FLOAT | High price |
| `low` | FLOAT | Low price |
| `close` | FLOAT | Closing price |
| `volume` | FLOAT | Trading volume |
| `dividend` | FLOAT | Dividend amount |
| `stock_splits` | FLOAT | Stock split ratio |

**Constraints**: Unique constraint on (symbol, time)

#### `market_stock_hist_bars_hour_ts`
**Purpose**: Hourly historical price data

| Column | Type | Description |
|--------|------|-------------|
| `symbol` | VARCHAR(10) | Stock symbol |
| `time` | TIMESTAMPTZ | Timestamp (TimescaleDB) |
| `open` | FLOAT | Opening price |
| `high` | FLOAT | High price |
| `low` | FLOAT | Low price |
| `close` | FLOAT | Closing price |
| `volume` | FLOAT | Trading volume |

### 3. Portfolio Management Tables

#### `portfolio`
**Purpose**: User portfolios

| Column | Type | Description |
|--------|------|-------------|
| `portfolio_id` | SERIAL | Primary key |
| `user_id` | INTEGER | Foreign key to auth_user |
| `name` | VARCHAR(100) | Portfolio name |
| `money_market` | DECIMAL(15,2) | Money market balance |
| `cash` | DECIMAL(15,2) | Cash balance |
| `investment` | DECIMAL(15,2) | Total investment |
| `margin_loan` | DECIMAL(15,2) | Margin loan amount |
| `is_default` | BOOLEAN | Default portfolio flag |
| `created_at` | TIMESTAMP | Creation timestamp |
| `updated_at` | TIMESTAMP | Last update timestamp |

#### `holding`
**Purpose**: Stock holdings in portfolios

| Column | Type | Description |
|--------|------|-------------|
| `holding_id` | SERIAL | Primary key |
| `portfolio_id` | INTEGER | Foreign key to portfolio |
| `symbol` | VARCHAR(20) | Foreign key to market_symbol |

**Constraints**: Unique constraint on (portfolio_id, symbol)

#### `transaction`
**Purpose**: Buy/sell transactions

| Column | Type | Description |
|--------|------|-------------|
| `transaction_id` | SERIAL | Primary key |
| `holding_id` | INTEGER | Foreign key to holding |
| `transaction_type` | VARCHAR(20) | BUY/SELL/DEPOSIT/WITHDRAW |
| `date` | TIMESTAMP | Transaction date |
| `quantity_final` | INTEGER | Final quantity |
| `price_final` | DECIMAL(10,2) | Final price |
| `commission` | DECIMAL(10,2) | Commission fee |
| `order_id` | INTEGER | Foreign key to order |
| `trade_id` | INTEGER | Foreign key to trade |

#### `order`
**Purpose**: Trading orders

| Column | Type | Description |
|--------|------|-------------|
| `order_id` | SERIAL | Primary key |
| `holding_id` | INTEGER | Foreign key to holding |
| `trade_id` | INTEGER | Foreign key to trade |
| `order_type` | VARCHAR(20) | MARKET/LIMIT/STOP/STOP_LIMIT |
| `quantity_target` | INTEGER | Target quantity |
| `price_market` | DECIMAL(10,2) | Market price |
| `price_stop` | DECIMAL(10,2) | Stop price |
| `price_limit` | DECIMAL(10,2) | Limit price |
| `action` | VARCHAR(20) | Action type |
| `timing` | VARCHAR(20) | Order timing |
| `order_style` | VARCHAR(20) | Order style |
| `ref_order_id` | INTEGER | Reference order |
| `wishlist_id` | INTEGER | Foreign key to wishlist |
| `is_obsolete` | BOOLEAN | Obsolete flag |
| `order_place_date` | TIMESTAMP | Order placement date |

### 4. Strategy and Screening Tables

#### `strategy`
**Purpose**: Trading strategies

| Column | Type | Description |
|--------|------|-------------|
| `strategy_id` | SERIAL | Primary key |
| `owner_user_id` | INTEGER | Foreign key to auth_user |
| `name` | VARCHAR(255) | Strategy name |
| `short_name` | VARCHAR(50) | Short name |
| `description` | TEXT | Strategy description |
| `as_of_date` | DATE | Strategy date |
| `custom_order` | INTEGER | Custom ordering |

#### `screening`
**Purpose**: Stock screening configurations

| Column | Type | Description |
|--------|------|-------------|
| `screening_id` | SERIAL | Primary key |
| `ref_screening_id` | INTEGER | Self-reference |
| `addendum_screening_id` | INTEGER | Addendum screening |
| `status` | VARCHAR(8) | Active/Deactivate |
| `name` | VARCHAR(255) | Screening name |
| `description` | TEXT | Description |
| `source` | VARCHAR(255) | Data source |
| `file_pattern` | VARCHAR(255) | File pattern |
| `import_models` | VARCHAR(255) | Import models |

#### `wishlist`
**Purpose**: Stock watchlist from screening results

| Column | Type | Description |
|--------|------|-------------|
| `wishlist_id` | SERIAL | Primary key |
| `symbol` | VARCHAR(20) | Foreign key to market_symbol |
| `add_by_id` | INTEGER | Foreign key to auth_user |
| `pick_at` | DATE | Pick date |
| `ref_strategy_id` | INTEGER | Foreign key to strategy |
| `ref_screening_id` | INTEGER | Foreign key to screening |
| `last_sync_time_hour` | TIMESTAMP | Last hour sync |
| `last_sync_time_ext_hour` | TIMESTAMP | Last extended hour sync |
| `last_sync_time_day` | TIMESTAMP | Last day sync |
| `order_position` | INTEGER | Order position |
| `bollinger_upper` | FLOAT | Bollinger upper band |
| `bollinger_lower` | FLOAT | Bollinger lower band |
| `rs_upper_max` | FLOAT | RS upper max |
| `rs_upper_min` | FLOAT | RS upper min |
| `rs_lower_max` | FLOAT | RS lower max |
| `rs_lower_min` | FLOAT | RS lower min |
| `rs_upper_max_2` | FLOAT | RS upper max 2 |
| `rs_upper_min_2` | FLOAT | RS upper min 2 |
| `rs_lower_max_2` | FLOAT | RS lower max 2 |
| `rs_lower_min_2` | FLOAT | RS lower min 2 |

### 5. Snapshot Tables (TimescaleDB)

#### `snapshot_screening`
**Purpose**: Time-series snapshots of screening results

| Column | Type | Description |
|--------|------|-------------|
| `symbol` | VARCHAR(20) | Foreign key to market_symbol |
| `time` | DATE | Snapshot date |
| `screening_id` | INTEGER | Foreign key to screening |

**Constraints**: Unique constraint on (symbol, time, screening_id)

#### `snapshot_overview`
**Purpose**: Overview snapshots

| Column | Type | Description |
|--------|------|-------------|
| `symbol` | VARCHAR(20) | Foreign key to market_symbol |
| `time` | DATE | Snapshot date |
| `name` | VARCHAR(255) | Company name |
| `setup_rating` | FLOAT | Setup rating |
| `technical_rating` | FLOAT | Technical rating |
| `fundamental_rating` | FLOAT | Fundamental rating |
| `relative_strength` | FLOAT | Relative strength |
| `one_month_performance` | FLOAT | 1-month performance |
| `three_month_performance` | FLOAT | 3-month performance |
| `six_month_performance` | FLOAT | 6-month performance |
| `percent_change` | FLOAT | Percent change |
| `price_earnings` | FLOAT | P/E ratio |
| `market_cap` | FLOAT | Market capitalization |
| `avg_volume_50` | FLOAT | 50-day average volume |

#### `snapshot_technical`
**Purpose**: Technical analysis snapshots

| Column | Type | Description |
|--------|------|-------------|
| `symbol` | VARCHAR(20) | Foreign key to market_symbol |
| `time` | DATE | Snapshot date |
| `lower_bollinger_band` | DECIMAL(20,2) | Lower Bollinger Band |
| `upper_bollinger_band` | DECIMAL(20,2) | Upper Bollinger Band |
| `RSI_14` | DECIMAL(20,2) | 14-period RSI |
| `MACD_12_26_9` | DECIMAL(20,2) | MACD indicator |
| `ADX_14` | DECIMAL(20,2) | 14-period ADX |
| `asset_turnover` | DECIMAL(20,2) | Asset turnover |
| `daily_effective_ratio` | DECIMAL(20,2) | Daily effective ratio |

#### `snapshot_fundamental`
**Purpose**: Fundamental analysis snapshots

| Column | Type | Description |
|--------|------|-------------|
| `symbol` | VARCHAR(20) | Foreign key to market_symbol |
| `time` | DATE | Snapshot date |
| `valuation_rating` | DECIMAL(20,2) | Valuation rating |
| `price_FCF` | DECIMAL(20,2) | Price to Free Cash Flow |
| `PEG_next_year` | DECIMAL(20,2) | PEG ratio |
| `growth_rating` | DECIMAL(20,2) | Growth rating |
| `EPS_growth_Q2Q` | DECIMAL(20,2) | EPS growth quarter to quarter |
| `profitability_rating` | DECIMAL(20,2) | Profitability rating |
| `high_growth_momentum_rating` | DECIMAL(20,2) | High growth momentum rating |
| `avg_ROIC_5y` | DECIMAL(20,2) | 5-year average ROIC |
| `FCF_margin` | DECIMAL(20,2) | Free Cash Flow margin |
| `health_rating` | DECIMAL(20,2) | Health rating |
| `interest_coverage` | DECIMAL(20,2) | Interest coverage |
| `shares_outstanding_5y_change` | DECIMAL(20,2) | 5-year shares outstanding change |

#### `snapshot_bull_flag`
**Purpose**: Bull flag pattern snapshots

| Column | Type | Description |
|--------|------|-------------|
| `symbol` | VARCHAR(20) | Foreign key to market_symbol |
| `time` | DATE | Snapshot date |
| `bull_indicator` | DECIMAL(20,2) | Bull indicator |
| `bull_flag` | BOOLEAN | Bull flag detected |
| `weekly_bull_flag` | BOOLEAN | Weekly bull flag |
| `bullish_engulfing_daily` | BOOLEAN | Daily bullish engulfing |
| `bullish_hammer_daily` | BOOLEAN | Daily bullish hammer |
| `bullish_harami_daily` | BOOLEAN | Daily bullish harami |
| `bullish_engulfing_weekly` | BOOLEAN | Weekly bullish engulfing |
| `bullish_hammer_weekly` | BOOLEAN | Weekly bullish hammer |
| `bullish_harami_weekly` | BOOLEAN | Weekly bullish harami |
| `flag_type` | DECIMAL(20,2) | Flag type |
| `flag_pole` | DECIMAL(20,2) | Flag pole |
| `flag_length` | DECIMAL(20,2) | Flag length |
| `flag_width` | DECIMAL(20,2) | Flag width |
| `weekly_flag_type` | DECIMAL(20,2) | Weekly flag type |

### 6. Rating and Analysis Tables

#### `rating`
**Purpose**: Strategy ratings for symbols

| Column | Type | Description |
|--------|------|-------------|
| `symbol` | VARCHAR(20) | Foreign key to market_symbol |
| `time` | DATE | Rating date |
| `strategy_id` | INTEGER | Foreign key to strategy |
| `score` | DECIMAL(5,2) | Rating score |

**Constraints**: Unique constraint on (symbol, time, strategy_id)

#### `rating_indicator_result`
**Purpose**: Technical indicator results

| Column | Type | Description |
|--------|------|-------------|
| `symbol` | VARCHAR(20) | Foreign key to market_symbol |
| `time` | DATE | Result date |
| `sma` | FLOAT | Simple Moving Average |
| `rsi` | FLOAT | RSI indicator |
| `bollinger_upper` | FLOAT | Bollinger upper band |
| `bollinger_lower` | FLOAT | Bollinger lower band |

### 7. User and System Tables

#### `user_static_setting`
**Purpose**: User trading preferences and settings

| Column | Type | Description |
|--------|------|-------------|
| `user_id` | INTEGER | Foreign key to auth_user (Primary key) |
| `capital` | DECIMAL(15,2) | Available capital |
| `risk` | DECIMAL(5,2) | Risk tolerance |
| `rounding` | INTEGER | Price rounding |
| `commission` | DECIMAL(10,2) | Commission rate |
| `tax` | DECIMAL(10,2) | Tax rate |
| `expect_gain_risk_ratio` | DECIMAL(5,2) | Expected gain/risk ratio |
| `position_min` | INTEGER | Minimum positions |
| `position_max` | INTEGER | Maximum positions |
| `total_risk_cap` | DECIMAL(5,2) | Total risk capital |
| `net_risk_cap` | DECIMAL(5,2) | Net risk capital |
| `performance_tracking_date` | DATE | Performance tracking start date |
| `single_max_drawdown` | DECIMAL(5,2) | Single max drawdown limit |

## Key Relationships

### Foreign Key Relationships
- `market_stock.symbol` → `market_symbol.symbol`
- `portfolio.user_id` → `auth_user.id`
- `holding.portfolio_id` → `portfolio.portfolio_id`
- `holding.symbol` → `market_symbol.symbol`
- `transaction.holding_id` → `holding.holding_id`
- `order.holding_id` → `holding.holding_id`
- `wishlist.symbol` → `market_symbol.symbol`
- `wishlist.ref_strategy_id` → `strategy.strategy_id`
- `snapshot_*.symbol` → `market_symbol.symbol`
- `rating.symbol` → `market_symbol.symbol`
- `rating.strategy_id` → `strategy.strategy_id`

### TimescaleDB Tables
The following tables use TimescaleDB for time-series optimization:
- `market_stock_hist_bars_min_ts`
- `market_stock_hist_bars_day_ts`
- `market_stock_hist_bars_hour_ts`
- `market_stock_hist_bars_hour_ext_ts`
- `snapshot_screening`
- `snapshot_overview`
- `snapshot_technical`
- `snapshot_fundamental`
- `snapshot_bull_flag`
- `snapshot_earning`
- `rating`
- `rating_indicator_result`
- `screening_operation`

## Indexes and Performance

### Primary Indexes
- All TimescaleDB tables have indexes on `(symbol, time)` for efficient time-series queries
- Unique constraints ensure data integrity for time-series data
- Foreign key indexes for join performance

### Query Optimization
- TimescaleDB compression for historical data
- Partitioning by time for large datasets
- Materialized views for complex aggregations

## Data Flow

1. **Market Data Ingestion**: Yahoo Finance API → TimescaleDB tables
2. **Screening Process**: Screening configurations → Wishlist → Orders
3. **Portfolio Management**: Orders → Transactions → Holdings → Portfolio updates
4. **Analysis**: Historical data → Snapshots → Ratings → Strategy decisions
5. **Trading Execution**: Orders → Interactive Brokers API → Transaction updates

## Security Considerations

- Database credentials stored in environment variables
- User authentication through Django's auth system
- Row-level security for user-specific data
- Encrypted connections for production database

## Backup and Maintenance

- Regular backups of PostgreSQL database
- TimescaleDB compression and retention policies
- Automated cleanup of old time-series data
- Monitoring of database performance and storage usage

---

*This documentation is generated for AI reference and should be updated when schema changes occur.*
