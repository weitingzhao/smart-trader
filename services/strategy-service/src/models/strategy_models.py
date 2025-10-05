from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional, Dict, Any

Base = declarative_base()

class Strategy(Base):
    """Strategy model for storing strategy configurations"""
    __tablename__ = 'strategies'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    strategy_class = Column(String(100), nullable=False)
    parameters = Column(JSON)  # Strategy parameters
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BacktestResult(Base):
    """Backtest result model"""
    __tablename__ = 'backtest_results'
    
    id = Column(Integer, primary_key=True)
    strategy_id = Column(Integer, nullable=False)
    symbol = Column(String(20), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    initial_capital = Column(Float, nullable=False)
    final_capital = Column(Float, nullable=False)
    total_return = Column(Float, nullable=False)
    sharpe_ratio = Column(Float)
    max_drawdown = Column(Float)
    win_rate = Column(Float)
    total_trades = Column(Integer)
    parameters = Column(JSON)  # Parameters used for this backtest
    created_at = Column(DateTime, default=datetime.utcnow)

class StrategyOptimization(Base):
    """Strategy optimization results"""
    __tablename__ = 'strategy_optimizations'
    
    id = Column(Integer, primary_key=True)
    strategy_id = Column(Integer, nullable=False)
    optimization_type = Column(String(50), nullable=False)  # 'parameter', 'walk_forward', etc.
    best_parameters = Column(JSON)
    best_performance = Column(JSON)
    optimization_results = Column(JSON)  # All optimization results
    created_at = Column(DateTime, default=datetime.utcnow)

class LiveStrategy(Base):
    """Live strategy execution tracking"""
    __tablename__ = 'live_strategies'
    
    id = Column(Integer, primary_key=True)
    strategy_id = Column(Integer, nullable=False)
    symbol = Column(String(20), nullable=False)
    is_running = Column(Boolean, default=False)
    start_time = Column(DateTime)
    last_update = Column(DateTime)
    current_position = Column(JSON)
    performance_metrics = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
