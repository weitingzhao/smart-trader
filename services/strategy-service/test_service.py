#!/usr/bin/env python3
"""
Strategy Service Test Script
Tests the refactored strategy service functionality
"""

import sys
import os
import asyncio
import logging
from datetime import datetime, timedelta

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_cerebro_base():
    """Test CerebroBase functionality"""
    try:
        from backtesting.cerebro_base import CerebroBase
        from strategies.three_step_strategy import ThreeStepStrategy
        
        logger.info("Testing CerebroBase...")
        
        # Create Cerebro instance
        cerebro = CerebroBase()
        
        # Test data fetching
        success = cerebro.set_data_from_yahoo(
            symbols="AAPL",
            period="1mo",
            since=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        )
        
        if success:
            logger.info("✅ Data fetching successful")
        else:
            logger.error("❌ Data fetching failed")
            return False
        
        # Test strategy setting
        cerebro.set_strategy(ThreeStepStrategy, trend_period=20, risk_ratio=2)
        logger.info("✅ Strategy setting successful")
        
        # Test configuration
        cerebro.configure(initial_cash=10000, commission=0.001)
        logger.info("✅ Configuration successful")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ CerebroBase test failed: {e}")
        return False

def test_three_step_strategy():
    """Test ThreeStepStrategy functionality"""
    try:
        from strategies.three_step_strategy import ThreeStepStrategy
        
        logger.info("Testing ThreeStepStrategy...")
        
        # Create strategy instance (this would normally be done by Backtrader)
        strategy = ThreeStepStrategy()
        
        # Test strategy info
        info = strategy.get_strategy_info()
        logger.info(f"✅ Strategy info: {info}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ ThreeStepStrategy test failed: {e}")
        return False

def test_optimization_service():
    """Test optimization service"""
    try:
        from services.optimization_service import StrategyOptimizationService
        
        logger.info("Testing OptimizationService...")
        
        # Create service
        service = StrategyOptimizationService()
        
        # Test sync optimization (without Ray for now)
        logger.info("✅ OptimizationService created successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ OptimizationService test failed: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints"""
    try:
        from api.strategy_api import router
        
        logger.info("Testing API endpoints...")
        
        # Check if router is properly configured
        routes = [route.path for route in router.routes]
        logger.info(f"✅ API routes: {routes}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ API endpoints test failed: {e}")
        return False

def test_main_app():
    """Test main FastAPI app"""
    try:
        from main import app
        
        logger.info("Testing main FastAPI app...")
        
        # Check if app is properly configured
        if app.title == "Smart Trader Strategy Service":
            logger.info("✅ FastAPI app configured correctly")
            return True
        else:
            logger.error("❌ FastAPI app configuration incorrect")
            return False
        
    except Exception as e:
        logger.error(f"❌ Main app test failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    logger.info("🚀 Starting Strategy Service Tests...")
    
    tests = [
        ("CerebroBase", test_cerebro_base),
        ("ThreeStepStrategy", test_three_step_strategy),
        ("OptimizationService", test_optimization_service),
        ("API Endpoints", test_api_endpoints),
        ("Main App", test_main_app)
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n--- Testing {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info("TEST SUMMARY")
    logger.info("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Strategy Service is ready.")
        return True
    else:
        logger.error(f"⚠️  {total - passed} tests failed. Please check the issues.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)