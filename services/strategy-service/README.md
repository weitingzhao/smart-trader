# Strategy Service - Smart Trader

## Overview
The Strategy Service handles all trading strategy development, backtesting, and optimization using the Backtrader framework. This service is designed to run on the GPU server (10.0.0.60) for optimal performance.

## Architecture

### Core Components
- **Strategies**: Trading strategy implementations
- **Indicators**: Custom technical indicators
- **Backtesting**: Backtrader integration and optimization
- **Services**: Business logic for strategy management
- **API**: FastAPI endpoints for strategy operations

### Key Features
- Multi-timeframe strategy analysis
- GPU-accelerated optimization with Ray
- Live trading strategy execution
- Custom indicator development
- Backtesting and performance analysis
- TradingView data integration

## Service Structure
```
strategy-service/
├── src/
│   ├── models/           # Strategy and backtesting models
│   ├── strategies/       # Trading strategies
│   ├── indicators/       # Custom indicators
│   ├── backtesting/      # Backtrader integration
│   ├── services/         # Business logic
│   ├── api/             # FastAPI endpoints
│   └── tasks/           # Celery tasks
├── tests/               # Unit tests
├── docs/                # Documentation
├── requirements.txt     # Dependencies
├── Dockerfile.gpu      # GPU-enabled container
└── main.py             # Service entry point
```

## Dependencies
- FastAPI for API endpoints
- Backtrader for strategy framework
- Ray for distributed optimization
- CUDA for GPU acceleration
- Redis for message queuing
- PostgreSQL for data storage
