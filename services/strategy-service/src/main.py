from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from dotenv import load_dotenv

from .api.strategy_api import router as strategy_router

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Smart Trader Strategy Service",
    version="1.0.0",
    description="Trading strategy development, backtesting, and optimization service",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(strategy_router, prefix="/api/strategy", tags=["strategy"])

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "strategy-service",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    try:
        # Check dependencies
        checks = {
            "redis": check_redis_connection(),
            "database": check_database_connection(),
            "data_service": check_data_service_connection()
        }
        
        all_ready = all(checks.values())
        
        return {
            "status": "ready" if all_ready else "not_ready",
            "service": "strategy-service",
            "checks": checks
        }
        
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return {
            "status": "not_ready",
            "service": "strategy-service",
            "error": str(e)
        }

@app.get("/metrics")
async def metrics():
    """Metrics endpoint for monitoring"""
    try:
        # This would collect actual metrics
        return {
            "service": "strategy-service",
            "metrics": {
                "active_backtests": 0,
                "active_optimizations": 0,
                "live_strategies": 0,
                "total_strategies": 1,
                "uptime": "1h 30m"
            }
        }
        
    except Exception as e:
        logger.error(f"Error collecting metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def check_redis_connection() -> bool:
    """Check Redis connection"""
    try:
        import redis
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        client = redis.from_url(redis_url)
        client.ping()
        return True
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        return False

def check_database_connection() -> bool:
    """Check database connection"""
    try:
        from sqlalchemy import create_engine
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            return False
        engine = create_engine(database_url)
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

def check_data_service_connection() -> bool:
    """Check data service connection"""
    try:
        import httpx
        data_service_url = os.getenv('DATA_SERVICE_URL', 'http://data-service:8000')
        with httpx.Client() as client:
            response = client.get(f"{data_service_url}/health", timeout=5.0)
            return response.status_code == 200
    except Exception as e:
        logger.error(f"Data service connection failed: {e}")
        return False

@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("Strategy Service starting up...")
    
    # Initialize services
    try:
        # Initialize Ray for distributed computing
        import ray
        if not ray.is_initialized():
            ray.init(ignore_reinit_error=True)
        logger.info("Ray initialized for distributed computing")
        
        # Initialize other services as needed
        logger.info("Strategy Service startup completed")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("Strategy Service shutting down...")
    
    try:
        # Cleanup Ray
        import ray
        if ray.is_initialized():
            ray.shutdown()
        logger.info("Ray shutdown completed")
        
        logger.info("Strategy Service shutdown completed")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    workers = int(os.getenv("WORKERS", 1))
    
    logger.info(f"Starting Strategy Service on {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        workers=workers,
        reload=os.getenv("ENVIRONMENT") == "development"
    )
