# Smart Trader Project Refactoring Plan

## 🎯 **Current Project Analysis**

### **Current Monolithic Structure**
```
smart-trader/
├── apps/                    # Django applications
│   ├── api/                # REST API endpoints
│   ├── common/             # Core models and utilities
│   ├── notifications/      # User notification system
│   ├── tasks/              # Celery task management
│   ├── file_manager/       # File management utilities
│   └── bokeh/              # Bokeh visualization
├── business/               # Business logic layer
│   ├── engines/            # Data processing engines
│   ├── services/           # Business services
│   ├── research/          # Research and analysis tools
│   ├── utilities/          # Utility functions
│   └── visualizes/         # Visualization tools
├── cerebro/                # Trading strategy framework
│   ├── strategy/           # Custom trading strategies
│   └── datafeed_tradingview/ # TradingView data integration
├── backtrader/             # Backtrader framework integration
├── home/                   # Main application views
├── ib/                     # Interactive Brokers integration
└── templates/              # Django templates
```

## 🏗️ **Target Multi-Service Architecture**

### **Service Distribution Strategy**
```
smart-trader-refactored/
├── services/
│   ├── data-service/           # Market data ingestion (10.0.0.75)
│   ├── portfolio-service/       # Portfolio management (10.0.0.80)
│   ├── strategy-service/        # Strategy development (10.0.0.60)
│   ├── execution-service/       # Order execution (10.0.0.80)
│   ├── risk-service/           # Risk management (10.0.0.80)
│   ├── ml-service/             # AI/ML trading (10.0.0.60)
│   ├── analytics-service/       # Advanced analytics (10.0.0.60)
│   ├── compliance-service/      # Regulatory compliance (10.0.0.80)
│   ├── news-service/           # News & sentiment (10.0.0.75)
│   ├── microstructure-service/ # Market microstructure (10.0.0.60)
│   ├── web-portal/             # User interface (10.0.0.75)
│   └── api-gateway/            # API gateway (10.0.0.75)
├── shared/
│   ├── models/                 # Shared data models
│   ├── utils/                 # Common utilities
│   ├── configs/               # Configuration files
│   └── schemas/               # API schemas
├── infrastructure/
│   ├── docker/                # Docker configurations
│   ├── kubernetes/            # K8s configurations
│   └── monitoring/            # Monitoring setup
└── docs/                      # Documentation
```

## 📋 **Refactoring Plan by Service**

### **Phase 1: Extract Data Service (Priority: HIGH)**

#### **Source Components to Extract:**
```
FROM: apps/common/models/market.py
FROM: apps/common/models/market_stock.py
FROM: business/services/fetching/
FROM: business/engines/
FROM: apps/tasks/controller/
```

#### **Target Service Structure:**
```
services/data-service/
├── src/
│   ├── models/
│   │   ├── market_symbol.py
│   │   ├── market_stock.py
│   │   └── historical_bars.py
│   ├── services/
│   │   ├── yahoo_finance_service.py
│   │   ├── data_ingestion_service.py
│   │   └── data_validation_service.py
│   ├── api/
│   │   ├── market_data_api.py
│   │   └── historical_data_api.py
│   └── tasks/
│       ├── data_fetching_tasks.py
│       └── data_processing_tasks.py
├── tests/
├── requirements.txt
├── Dockerfile
└── main.py
```

#### **Migration Steps:**
1. **Extract Models**: Move market-related models from `apps/common/models/`
2. **Extract Services**: Move data fetching services from `business/services/fetching/`
3. **Extract Tasks**: Move data-related Celery tasks from `apps/tasks/`
4. **Create API**: Build FastAPI endpoints for data access
5. **Update Dependencies**: Remove Django dependencies, add FastAPI

### **Phase 2: Extract Portfolio Service (Priority: HIGH)**

#### **Source Components to Extract:**
```
FROM: apps/common/models/portfolio.py
FROM: apps/common/models/wishlist.py
FROM: home/views/position/
FROM: home/views/cash_flow/
FROM: business/researchs/position/
```

#### **Target Service Structure:**
```
services/portfolio-service/
├── src/
│   ├── models/
│   │   ├── portfolio.py
│   │   ├── holding.py
│   │   ├── transaction.py
│   │   └── wishlist.py
│   ├── services/
│   │   ├── portfolio_service.py
│   │   ├── position_service.py
│   │   ├── transaction_service.py
│   │   └── cash_flow_service.py
│   ├── api/
│   │   ├── portfolio_api.py
│   │   ├── position_api.py
│   │   └── transaction_api.py
│   └── calculations/
│       ├── pnl_calculator.py
│       └── performance_calculator.py
├── tests/
├── requirements.txt
├── Dockerfile
└── main.py
```

### **Phase 3: Extract Strategy Service (Priority: HIGH)**

#### **Source Components to Extract:**
```
FROM: cerebro/
FROM: backtrader/
FROM: business/researchs/
FROM: apps/common/models/strategy.py
FROM: apps/common/models/screening.py
```

#### **Target Service Structure:**
```
services/strategy-service/
├── src/
│   ├── models/
│   │   ├── strategy.py
│   │   ├── screening.py
│   │   └── rating.py
│   ├── strategies/
│   │   ├── three_step_strategy.py
│   │   ├── live_strategy.py
│   │   └── strategy1stoperation.py
│   ├── indicators/
│   │   ├── bollinger/
│   │   ├── macd/
│   │   └── reinforcement/
│   ├── backtesting/
│   │   ├── cerebro_base.py
│   │   ├── ray_optimize.py
│   │   └── backtesting_engine.py
│   ├── services/
│   │   ├── strategy_service.py
│   │   ├── backtesting_service.py
│   │   └── optimization_service.py
│   └── api/
│       ├── strategy_api.py
│       └── backtesting_api.py
├── tests/
├── requirements.txt
├── Dockerfile.gpu
└── main.py
```

### **Phase 4: Extract Risk Service (Priority: HIGH)**

#### **Source Components to Extract:**
```
FROM: apps/common/models/main.py (UserStaticSetting)
FROM: business/researchs/position/open_position.py
FROM: business/researchs/position/close_position.py
FROM: apps/common/models/market_stock.py (RiskMetrics)
```

#### **Target Service Structure:**
```
services/risk-service/
├── src/
│   ├── models/
│   │   ├── risk_settings.py
│   │   ├── risk_metrics.py
│   │   └── compliance_rules.py
│   ├── calculations/
│   │   ├── var_calculator.py
│   │   ├── drawdown_calculator.py
│   │   ├── correlation_analyzer.py
│   │   └── position_sizing.py
│   ├── monitoring/
│   │   ├── risk_monitor.py
│   │   ├── alert_system.py
│   │   └── compliance_checker.py
│   ├── services/
│   │   ├── risk_service.py
│   │   ├── portfolio_risk_service.py
│   │   └── compliance_service.py
│   └── api/
│       ├── risk_api.py
│       └── compliance_api.py
├── tests/
├── requirements.txt
├── Dockerfile
└── main.py
```

### **Phase 5: Extract ML Service (Priority: MEDIUM)**

#### **Source Components to Extract:**
```
FROM: cerebro/strategy/indicator/reinforcement/
FROM: business/researchs/treading/trading_research.py
FROM: business/researchs/patterns/
```

#### **Target Service Structure:**
```
services/ml-service/
├── src/
│   ├── models/
│   │   ├── ml_model.py
│   │   └── training_data.py
│   ├── ml/
│   │   ├── pattern_recognition.py
│   │   ├── sentiment_analysis.py
│   │   ├── price_prediction.py
│   │   └── reinforcement_learning.py
│   ├── features/
│   │   ├── technical_features.py
│   │   ├── fundamental_features.py
│   │   └── market_features.py
│   ├── services/
│   │   ├── ml_service.py
│   │   ├── training_service.py
│   │   └── prediction_service.py
│   └── api/
│       ├── ml_api.py
│       └── training_api.py
├── tests/
├── requirements.txt
├── Dockerfile.gpu
└── main.py
```

### **Phase 6: Extract Web Portal (Priority: MEDIUM)**

#### **Source Components to Extract:**
```
FROM: home/
FROM: apps/bokeh/
FROM: templates/
FROM: static/
FROM: apps/notifications/
```

#### **Target Service Structure:**
```
services/web-portal/
├── src/
│   ├── views/
│   │   ├── dashboard/
│   │   ├── analytics/
│   │   ├── performance/
│   │   └── settings/
│   ├── templates/
│   ├── static/
│   ├── websockets/
│   └── notifications/
├── tests/
├── requirements.txt
├── Dockerfile
└── main.py
```

### **Phase 7: Extract Execution Service (Priority: MEDIUM)**

#### **Source Components to Extract:**
```
FROM: ib/
FROM: apps/common/models/portfolio.py (Order, Transaction)
FROM: business/services/
```

#### **Target Service Structure:**
```
services/execution-service/
├── src/
│   ├── models/
│   │   ├── order.py
│   │   ├── execution.py
│   │   └── broker_connection.py
│   ├── brokers/
│   │   ├── interactive_brokers.py
│   │   ├── alpaca.py
│   │   └── broker_interface.py
│   ├── services/
│   │   ├── execution_service.py
│   │   ├── order_management.py
│   │   └── broker_service.py
│   └── api/
│       ├── execution_api.py
│       └── order_api.py
├── tests/
├── requirements.txt
├── Dockerfile
└── main.py
```

## 🔄 **Refactoring Implementation Steps**

### **Step 1: Create Shared Package**
```bash
mkdir -p shared/{models,utils,configs,schemas}
```

#### **Extract Common Models:**
```python
# shared/models/base.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BaseEntity(BaseModel):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class MarketSymbol(BaseEntity):
    symbol: str
    name: str
    market: str
    asset_type: str
    # ... other fields

class Portfolio(BaseEntity):
    user_id: int
    name: str
    money_market: float
    cash: float
    investment: float
    # ... other fields
```

#### **Extract Common Utilities:**
```python
# shared/utils/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

def get_database_connection():
    database_url = os.getenv('DATABASE_URL')
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

# shared/utils/redis.py
import redis
import os

def get_redis_connection():
    redis_url = os.getenv('REDIS_URL')
    return redis.from_url(redis_url)
```

### **Step 2: Create Service Templates**
```bash
mkdir -p services/template-service/{src,tests,docs}
```

#### **Service Template Structure:**
```python
# services/template-service/src/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Smart Trader Service",
    version="1.0.0",
    description="Template service for Smart Trader"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": os.getenv("SERVICE_NAME", "template-service")}

@app.get("/ready")
async def readiness_check():
    return {"status": "ready", "service": os.getenv("SERVICE_NAME", "template-service")}

@app.get("/metrics")
async def metrics():
    return {"metrics": "placeholder"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### **Step 3: Extract Data Service (First Service)**

#### **Create Data Service Structure:**
```bash
mkdir -p services/data-service/{src,tests,docs}
mkdir -p services/data-service/src/{models,services,api,tasks}
```

#### **Extract Market Models:**
```python
# services/data-service/src/models/market_symbol.py
from sqlalchemy import Column, String, Date, Boolean, Integer
from sqlalchemy.ext.declarative import declarative_base
from shared.models.base import BaseEntity

Base = declarative_base()

class MarketSymbol(Base):
    __tablename__ = 'market_symbol'
    
    symbol = Column(String(20), primary_key=True)
    name = Column(String(200))
    market = Column(String(50))
    asset_type = Column(String(50))
    ipo_date = Column(Date)
    delisting_date = Column(Date)
    status = Column(String(20))
    has_company_info = Column(Boolean, default=False)
    is_delisted = Column(Boolean, default=False)
    min_period_yfinance = Column(String(20))
    daily_period_yfinance = Column(String(20))
```

#### **Extract Data Services:**
```python
# services/data-service/src/services/yahoo_finance_service.py
import yfinance as yf
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class YahooFinanceService:
    def __init__(self):
        self.logger = logger
    
    def get_historical_data(self, symbol: str, period: str = "1y") -> Dict[str, Any]:
        """Get historical data for a symbol"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            return data.to_dict()
        except Exception as e:
            self.logger.error(f"Error fetching data for {symbol}: {e}")
            return {}
    
    def get_company_info(self, symbol: str) -> Dict[str, Any]:
        """Get company information"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return info
        except Exception as e:
            self.logger.error(f"Error fetching company info for {symbol}: {e}")
            return {}
```

#### **Create Data API:**
```python
# services/data-service/src/api/market_data_api.py
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from ..services.yahoo_finance_service import YahooFinanceService

router = APIRouter()
yahoo_service = YahooFinanceService()

@router.get("/historical/{symbol}")
async def get_historical_data(symbol: str, period: str = "1y"):
    """Get historical data for a symbol"""
    data = yahoo_service.get_historical_data(symbol, period)
    if not data:
        raise HTTPException(status_code=404, detail="Data not found")
    return data

@router.get("/company/{symbol}")
async def get_company_info(symbol: str):
    """Get company information"""
    info = yahoo_service.get_company_info(symbol)
    if not info:
        raise HTTPException(status_code=404, detail="Company info not found")
    return info
```

### **Step 4: Update Dependencies**

#### **Data Service Requirements:**
```txt
# services/data-service/requirements.txt
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
redis==5.0.1
pandas==2.1.4
numpy==1.24.3
yfinance==0.2.54
python-dotenv==1.0.0
celery==5.3.4
```

#### **Remove Django Dependencies:**
- Remove Django-specific imports
- Replace Django models with SQLAlchemy
- Replace Django REST framework with FastAPI
- Update database connections

### **Step 5: Create Service Communication**

#### **API Gateway Configuration:**
```python
# services/api-gateway/src/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os

app = FastAPI(title="Smart Trader API Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs
SERVICE_URLS = {
    "data-service": os.getenv("DATA_SERVICE_URL", "http://10.0.0.75:8001"),
    "portfolio-service": os.getenv("PORTFOLIO_SERVICE_URL", "http://10.0.0.80:8002"),
    "strategy-service": os.getenv("STRATEGY_SERVICE_URL", "http://10.0.0.60:8003"),
    "risk-service": os.getenv("RISK_SERVICE_URL", "http://10.0.0.80:8004"),
    "ml-service": os.getenv("ML_SERVICE_URL", "http://10.0.0.60:8005"),
}

@app.get("/api/data/{path:path}")
async def proxy_data_service(path: str):
    """Proxy requests to data service"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{SERVICE_URLS['data-service']}/{path}")
        return response.json()

@app.get("/api/portfolio/{path:path}")
async def proxy_portfolio_service(path: str):
    """Proxy requests to portfolio service"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{SERVICE_URLS['portfolio-service']}/{path}")
        return response.json()
```

## 📊 **Migration Timeline**

### **Week 1-2: Foundation**
- Create shared package
- Set up service templates
- Create API gateway

### **Week 3-4: Data Service**
- Extract market models
- Extract data services
- Create data API
- Test data service

### **Week 5-6: Portfolio Service**
- Extract portfolio models
- Extract portfolio services
- Create portfolio API
- Test portfolio service

### **Week 7-8: Strategy Service**
- Extract strategy models
- Extract backtrader integration
- Create strategy API
- Test strategy service

### **Week 9-10: Risk Service**
- Extract risk models
- Extract risk calculations
- Create risk API
- Test risk service

### **Week 11-12: ML Service**
- Extract ML components
- Extract pattern recognition
- Create ML API
- Test ML service

### **Week 13-14: Web Portal**
- Extract web components
- Extract Bokeh visualizations
- Create web portal
- Test web portal

### **Week 15-16: Execution Service**
- Extract execution components
- Extract broker integrations
- Create execution API
- Test execution service

## 🎯 **Benefits of Refactoring**

### **Technical Benefits**
- **Independent scaling** of services
- **Technology flexibility** per service
- **Easier testing** and debugging
- **Better maintainability**

### **Operational Benefits**
- **Fault isolation** - one service failure doesn't affect others
- **Independent deployment** - deploy services separately
- **Resource optimization** - allocate resources based on service needs
- **Team scalability** - different teams can work on different services

### **Business Benefits**
- **Faster development** cycles
- **Better performance** through optimization
- **Easier compliance** with regulatory requirements
- **Scalable architecture** for future growth

## 🚀 **Next Steps**

1. **Start with shared package** - Extract common models and utilities
2. **Create service templates** - Standardize service structure
3. **Extract data service first** - Most independent component
4. **Set up API gateway** - Centralized routing
5. **Gradually extract other services** - One at a time
6. **Test each service** - Ensure functionality before moving to next
7. **Update documentation** - Keep docs in sync with changes

This refactoring plan transforms your monolithic Django application into a scalable microservices architecture optimized for your local hardware environment.
