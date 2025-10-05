#!/bin/bash
# Smart Trader Project Refactoring Script

echo "🔄 Starting Smart Trader Project Refactoring..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Create backup of current project
create_backup() {
    print_header "Creating Backup of Current Project"
    
    BACKUP_DIR="../smart-trader-backup-$(date +%Y%m%d-%H%M%S)"
    print_status "Creating backup at: $BACKUP_DIR"
    
    cp -r . "$BACKUP_DIR"
    print_status "✅ Backup created successfully"
}

# Create shared package structure
create_shared_package() {
    print_header "Creating Shared Package Structure"
    
    mkdir -p shared/{models,utils,configs,schemas}
    
    # Create base model
    cat > shared/models/__init__.py << 'EOF'
from .base import BaseEntity, BaseModel
from .market_symbol import MarketSymbol
from .portfolio import Portfolio, Holding, Transaction

__all__ = [
    'BaseEntity',
    'BaseModel', 
    'MarketSymbol',
    'Portfolio',
    'Holding',
    'Transaction'
]
EOF

    # Create base model
    cat > shared/models/base.py << 'EOF'
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BaseModel(BaseModel):
    """Base Pydantic model for all entities"""
    class Config:
        from_attributes = True

class BaseEntity(BaseModel):
    """Base entity with common fields"""
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
EOF

    # Create market symbol model
    cat > shared/models/market_symbol.py << 'EOF'
from typing import Optional
from datetime import date
from .base import BaseEntity

class MarketSymbol(BaseEntity):
    symbol: str
    name: str
    market: str
    asset_type: str
    ipo_date: Optional[date] = None
    delisting_date: Optional[date] = None
    status: str
    has_company_info: bool = False
    is_delisted: bool = False
    min_period_yfinance: Optional[str] = None
    daily_period_yfinance: Optional[str] = None
EOF

    # Create portfolio models
    cat > shared/models/portfolio.py << 'EOF'
from typing import Optional, List
from datetime import datetime
from .base import BaseEntity

class Portfolio(BaseEntity):
    user_id: int
    name: str
    money_market: float = 0.0
    cash: float = 0.0
    investment: float = 0.0
    margin_loan: float = 0.0
    is_default: bool = False

class Holding(BaseEntity):
    portfolio_id: int
    symbol: str
    quantity: int
    average_price: float

class Transaction(BaseEntity):
    holding_id: int
    transaction_type: str  # BUY, SELL, DEPOSIT, WITHDRAW
    date: datetime
    quantity: int
    price: float
    commission: float = 0.0
EOF

    # Create utils
    cat > shared/utils/__init__.py << 'EOF'
from .database import get_database_connection
from .redis import get_redis_connection
from .config import get_config

__all__ = [
    'get_database_connection',
    'get_redis_connection', 
    'get_config'
]
EOF

    cat > shared/utils/database.py << 'EOF'
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

def get_database_connection():
    """Get database connection"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")
    
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def get_database_engine():
    """Get database engine"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")
    
    return create_engine(database_url)
EOF

    cat > shared/utils/redis.py << 'EOF'
import redis
import os

def get_redis_connection():
    """Get Redis connection"""
    redis_url = os.getenv('REDIS_URL')
    if not redis_url:
        raise ValueError("REDIS_URL environment variable not set")
    
    return redis.from_url(redis_url)
EOF

    cat > shared/utils/config.py << 'EOF'
import os
from typing import Dict, Any

def get_config() -> Dict[str, Any]:
    """Get configuration from environment variables"""
    return {
        'database_url': os.getenv('DATABASE_URL'),
        'redis_url': os.getenv('REDIS_URL'),
        'service_name': os.getenv('SERVICE_NAME'),
        'environment': os.getenv('ENVIRONMENT', 'development'),
        'debug': os.getenv('DEBUG', 'False').lower() == 'true'
    }
EOF

    # Create shared requirements
    cat > shared/requirements.txt << 'EOF'
pydantic==2.5.0
sqlalchemy==2.0.23
redis==5.0.1
python-dotenv==1.0.0
EOF

    print_status "✅ Shared package structure created"
}

# Create service templates
create_service_templates() {
    print_header "Creating Service Templates"
    
    mkdir -p services/template-service/{src,tests,docs}
    mkdir -p services/template-service/src/{models,services,api,tasks}
    
    # Create main.py template
    cat > services/template-service/src/main.py << 'EOF'
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
EOF

    # Create Dockerfile template
    cat > services/template-service/Dockerfile << 'EOF'
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy shared package
COPY ../../shared /app/shared
RUN pip install -e /app/shared

# Copy application code
COPY . /app

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "src/main.py"]
EOF

    # Create requirements template
    cat > services/template-service/requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
redis==5.0.1
pandas==2.1.4
numpy==1.24.3
python-dotenv==1.0.0
celery==5.3.4
EOF

    # Create test template
    cat > services/template-service/tests/test_main.py << 'EOF'
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_readiness_check():
    response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"

def test_metrics():
    response = client.get("/metrics")
    assert response.status_code == 200
EOF

    print_status "✅ Service templates created"
}

# Extract data service
extract_data_service() {
    print_header "Extracting Data Service"
    
    mkdir -p services/data-service/{src,tests,docs}
    mkdir -p services/data-service/src/{models,services,api,tasks}
    
    # Copy template to data service
    cp -r services/template-service/* services/data-service/
    
    # Create data service specific files
    cat > services/data-service/src/models/__init__.py << 'EOF'
from .market_symbol import MarketSymbol
from .market_stock import MarketStock
from .historical_bars import HistoricalBars

__all__ = ['MarketSymbol', 'MarketStock', 'HistoricalBars']
EOF

    cat > services/data-service/src/models/market_symbol.py << 'EOF'
from sqlalchemy import Column, String, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base

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
EOF

    cat > services/data-service/src/services/yahoo_finance_service.py << 'EOF'
import yfinance as yf
from typing import Dict, Any, List
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
    
    def get_multiple_symbols(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get data for multiple symbols"""
        try:
            tickers = yf.Tickers(" ".join(symbols))
            result = {}
            for symbol in symbols:
                result[symbol] = tickers.tickers[symbol].info
            return result
        except Exception as e:
            self.logger.error(f"Error fetching multiple symbols: {e}")
            return {}
EOF

    cat > services/data-service/src/api/market_data_api.py << 'EOF'
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

@router.get("/symbols")
async def get_multiple_symbols(symbols: str):
    """Get data for multiple symbols (comma-separated)"""
    symbol_list = symbols.split(",")
    data = yahoo_service.get_multiple_symbols(symbol_list)
    if not data:
        raise HTTPException(status_code=404, detail="No data found")
    return data
EOF

    # Update main.py for data service
    cat > services/data-service/src/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from .api.market_data_api import router as market_data_router

load_dotenv()

app = FastAPI(
    title="Smart Trader Data Service",
    version="1.0.0",
    description="Market data ingestion and management service"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(market_data_router, prefix="/api/market", tags=["market"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "data-service"}

@app.get("/ready")
async def readiness_check():
    return {"status": "ready", "service": "data-service"}

@app.get("/metrics")
async def metrics():
    return {"metrics": "placeholder"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

    # Update requirements for data service
    cat > services/data-service/requirements.txt << 'EOF'
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
EOF

    print_status "✅ Data service extracted"
}

# Create API gateway
create_api_gateway() {
    print_header "Creating API Gateway"
    
    mkdir -p services/api-gateway/{src,tests,docs}
    
    # Copy template to API gateway
    cp -r services/template-service/* services/api-gateway/
    
    # Create API gateway specific files
    cat > services/api-gateway/src/main.py << 'EOF'
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Smart Trader API Gateway",
    version="1.0.0",
    description="API Gateway for Smart Trader services"
)

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
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{SERVICE_URLS['data-service']}/{path}")
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/portfolio/{path:path}")
async def proxy_portfolio_service(path: str):
    """Proxy requests to portfolio service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{SERVICE_URLS['portfolio-service']}/{path}")
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/strategy/{path:path}")
async def proxy_strategy_service(path: str):
    """Proxy requests to strategy service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{SERVICE_URLS['strategy-service']}/{path}")
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/risk/{path:path}")
async def proxy_risk_service(path: str):
    """Proxy requests to risk service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{SERVICE_URLS['risk-service']}/{path}")
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ml/{path:path}")
async def proxy_ml_service(path: str):
    """Proxy requests to ML service"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{SERVICE_URLS['ml-service']}/{path}")
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "api-gateway"}

@app.get("/ready")
async def readiness_check():
    return {"status": "ready", "service": "api-gateway"}

@app.get("/metrics")
async def metrics():
    return {"metrics": "placeholder"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

    # Update requirements for API gateway
    cat > services/api-gateway/requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn==0.24.0
httpx==0.25.2
python-dotenv==1.0.0
EOF

    print_status "✅ API Gateway created"
}

# Create Docker Compose for services
create_docker_compose() {
    print_header "Creating Docker Compose for Services"
    
    cat > docker-compose.services.yml << 'EOF'
version: '3.8'

services:
  # Shared Infrastructure
  postgres:
    image: timescale/timescaledb:latest-pg17
    container_name: smart-trader.postgres
    environment:
      POSTGRES_DB: smart_trader_refactored
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: refactored_password
      TIMESCALEDB_TELEMETRY: off
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - smart-trader-network

  redis:
    image: redis:7.0.12
    container_name: smart-trader.redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - smart-trader-network
    command: ["redis-server", "--appendonly", "yes"]

  # Data Service (10.0.0.75)
  data-service:
    build: 
      context: ./services/data-service
      dockerfile: Dockerfile
    container_name: smart-trader.data-service
    ports:
      - "8001:8000"
    environment:
      - SERVICE_NAME=data-service
      - DATABASE_URL=postgresql://postgres:refactored_password@postgres:5432/smart_trader_refactored
      - REDIS_URL=redis://redis:6379
      - ENVIRONMENT=development
    depends_on:
      - postgres
      - redis
    networks:
      - smart-trader-network

  # API Gateway (10.0.0.75)
  api-gateway:
    build: 
      context: ./services/api-gateway
      dockerfile: Dockerfile
    container_name: smart-trader.api-gateway
    ports:
      - "8080:8000"
    environment:
      - SERVICE_NAME=api-gateway
      - DATA_SERVICE_URL=http://data-service:8000
      - PORTFOLIO_SERVICE_URL=http://portfolio-service:8000
      - STRATEGY_SERVICE_URL=http://strategy-service:8000
      - RISK_SERVICE_URL=http://risk-service:8000
      - ML_SERVICE_URL=http://ml-service:8000
    depends_on:
      - data-service
    networks:
      - smart-trader-network

networks:
  smart-trader-network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
EOF

    print_status "✅ Docker Compose for services created"
}

# Create development scripts
create_dev_scripts() {
    print_header "Creating Development Scripts"
    
    # Create service development script
    cat > scripts/dev-services.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Smart Trader Services Development Environment..."

# Start shared infrastructure
echo "Starting shared infrastructure..."
docker-compose -f docker-compose.services.yml up -d postgres redis

# Wait for infrastructure to be ready
echo "Waiting for infrastructure to be ready..."
sleep 10

# Start data service
echo "Starting data service..."
docker-compose -f docker-compose.services.yml up -d data-service

# Wait for data service to be ready
echo "Waiting for data service to be ready..."
sleep 5

# Start API gateway
echo "Starting API gateway..."
docker-compose -f docker-compose.services.yml up -d api-gateway

echo "✅ Services started successfully!"
echo "Services available at:"
echo "- Data Service: http://localhost:8001"
echo "- API Gateway: http://localhost:8080"
echo "- PostgreSQL: localhost:5432"
echo "- Redis: localhost:6379"
EOF

    chmod +x scripts/dev-services.sh
    
    # Create test script
    cat > scripts/test-services.sh << 'EOF'
#!/bin/bash
echo "🧪 Testing Smart Trader Services..."

# Test data service
echo "Testing data service..."
curl -f http://localhost:8001/health || echo "❌ Data service health check failed"

# Test API gateway
echo "Testing API gateway..."
curl -f http://localhost:8080/health || echo "❌ API gateway health check failed"

# Test data service through API gateway
echo "Testing data service through API gateway..."
curl -f "http://localhost:8080/api/data/historical/AAPL?period=1mo" || echo "❌ Data service proxy failed"

echo "✅ Service tests completed!"
EOF

    chmod +x scripts/test-services.sh
    
    print_status "✅ Development scripts created"
}

# Main execution
main() {
    print_header "Smart Trader Project Refactoring"
    
    create_backup
    create_shared_package
    create_service_templates
    extract_data_service
    create_api_gateway
    create_docker_compose
    create_dev_scripts
    
    print_header "Refactoring Complete!"
    print_status "✅ Backup created"
    print_status "✅ Shared package created"
    print_status "✅ Service templates created"
    print_status "✅ Data service extracted"
    print_status "✅ API gateway created"
    print_status "✅ Docker Compose created"
    print_status "✅ Development scripts created"
    
    echo ""
    print_status "Next steps:"
    echo "1. Run ./scripts/dev-services.sh to start services"
    echo "2. Run ./scripts/test-services.sh to test services"
    echo "3. Extract portfolio service next"
    echo "4. Extract strategy service"
    echo "5. Extract risk service"
    echo "6. Extract ML service"
    
    echo ""
    print_warning "Remember to:"
    echo "- Update environment variables"
    echo "- Test each service before moving to next"
    echo "- Update documentation as you go"
    echo "- Keep the original project as backup"
}

# Run main function
main "$@"
