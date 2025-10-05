import backtrader as bt
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class ThreeStepStrategy(bt.Strategy):
    """
    Three-step trading strategy with multi-timeframe analysis:
    1. Daily trend identification (有序行为)
    2. Hourly signal validation (关键动作) 
    3. Entry execution (低成本入场)
    """
    
    params = (
        ('trend_period', 20),    # Trend identification period
        ('entry_period', 10),    # Entry signal period
        ('atr_period', 14),      # ATR period
        ('risk_ratio', 3),       # Risk-reward ratio
        ('volume_threshold', 1.2), # Volume threshold multiplier
        ('consolidation_threshold', 0.3), # Consolidation ATR threshold
    )

    def __init__(self):
        # Multi-timeframe data preparation
        self.daily = self.datas[0]
        self.hourly = self.datas[1] if len(self.datas) > 1 else self.datas[0]

        # Step 1: Ordered behavior indicators (Daily timeframe)
        self.daily_sma = bt.indicators.SMA(self.daily.close, period=self.p.trend_period)
        self.daily_boll = bt.indicators.BollingerBands(self.daily.close, period=self.p.trend_period)
        self.daily_rsi = bt.indicators.RSI(self.daily.close, period=14)

        # Step 2: Key action indicators (Hourly timeframe)
        self.hourly_ema = bt.indicators.EMA(self.hourly.close, period=self.p.entry_period)
        self.hourly_atr = bt.indicators.ATR(self.hourly, period=self.p.atr_period)

        # Step 3: Entry signal indicators
        self.crossover = bt.indicators.CrossOver(self.hourly.close, self.hourly_ema)

        # Strategy state
        self.trend_type = None
        self.entry_price = 0
        self.stop_loss = 0
        self.take_profit = 0
        self.trade_count = 0
        
        logger.info("ThreeStepStrategy initialized")

    def next(self):
        """Main strategy logic"""
        try:
            if not self.position:  # No position - look for entry
                # Step 1: Check ordered behavior
                daily_condition = self.check_daily_trend()
                if daily_condition:
                    # Step 2: Validate key action
                    hourly_condition = self.check_hourly_signal(daily_condition)
                    if hourly_condition:
                        # Step 3: Execute low-cost entry
                        self.execute_entry(daily_condition)
            else:  # Have position - monitor exit conditions
                self.monitor_exit()
                
        except Exception as e:
            logger.error(f"Error in strategy next(): {e}")

    def check_daily_trend(self) -> Optional[str]:
        """Step 1: Identify daily trend type"""
        try:
            # Get current values
            price = self.daily.close[0]
            sma = self.daily_sma[0]
            boll_top = self.daily_boll.lines.top[0]
            boll_bot = self.daily_boll.lines.bot[0]
            rsi = self.daily_rsi[0]
            
            # Trend conditions
            price_above_sma = price > sma
            price_in_upper = price > boll_top
            price_in_lower = price < boll_bot
            rsi_overbought = rsi > 70
            rsi_oversold = rsi < 30
            
            # Bollinger band width (for consolidation detection)
            current_width = boll_top - boll_bot
            prev_width = self.daily_boll.lines.top[-1] - self.daily_boll.lines.bot[-1]
            
            # Determine trend type
            if price_above_sma and price_in_upper:
                logger.debug("Daily trend: Breakout detected")
                return 'breakout'
            elif current_width < prev_width:
                logger.debug("Daily trend: Consolidation detected")
                return 'consolidation'
            elif (price_in_lower and rsi_oversold) or (price_in_upper and rsi_overbought):
                logger.debug("Daily trend: Reversal detected")
                return 'reversal'
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking daily trend: {e}")
            return None

    def check_hourly_signal(self, trend_type: str) -> bool:
        """Step 2: Validate hourly signal"""
        try:
            if trend_type == 'breakout':
                # Volume confirmation for breakout
                volume_confirmation = self.hourly.volume[0] > self.hourly.volume[-1] * self.p.volume_threshold
                price_above_ema = self.hourly.close[0] > self.hourly_ema[0]
                return price_above_ema and volume_confirmation
                
            elif trend_type == 'consolidation':
                # Narrow range for consolidation
                body_size = abs(self.hourly.close[0] - self.hourly.open[0])
                return body_size < self.hourly_atr[0] * self.p.consolidation_threshold
                
            elif trend_type == 'reversal':
                # Crossover signal for reversal
                return self.crossover[0] != 0
                
            return False
            
        except Exception as e:
            logger.error(f"Error checking hourly signal: {e}")
            return False

    def execute_entry(self, trend_type: str):
        """Step 3: Execute entry with risk management"""
        try:
            # Calculate position size
            available_cash = self.broker.getcash() * 0.98
            current_price = self.hourly.close[0]
            size = available_cash / current_price
            
            # Set entry parameters based on trend type
            if trend_type == 'breakout':
                self._execute_breakout_entry(size, current_price)
            elif trend_type == 'reversal':
                self._execute_reversal_entry(size, current_price)
            elif trend_type == 'consolidation':
                self._execute_consolidation_entry(size, current_price)
            
            self.trade_count += 1
            logger.info(f"Entry executed for {trend_type} trend, trade #{self.trade_count}")
            
        except Exception as e:
            logger.error(f"Error executing entry: {e}")

    def _execute_breakout_entry(self, size: float, current_price: float):
        """Execute breakout entry"""
        atr = self.hourly_atr[0]
        
        # Entry price slightly above low
        entry_price = self.hourly.low[0] + atr * 0.2
        
        # Stop loss below recent low
        self.stop_loss = self.hourly.low[0] - atr * 0.5
        
        # Take profit based on risk ratio
        self.take_profit = entry_price + (entry_price - self.stop_loss) * self.p.risk_ratio
        
        # Execute bracket order
        self.buy_bracket(
            price=entry_price,
            size=size,
            stopprice=self.stop_loss,
            limitprice=self.take_profit,
            exectype=bt.Order.StopLimit
        )

    def _execute_reversal_entry(self, size: float, current_price: float):
        """Execute reversal entry"""
        atr = self.hourly_atr[0]
        
        # Entry at current price
        entry_price = current_price
        
        # Stop loss below entry
        self.stop_loss = entry_price - atr * 1.5
        
        # Take profit based on risk ratio
        self.take_profit = entry_price + (entry_price - self.stop_loss) * self.p.risk_ratio
        
        # Execute bracket order
        self.buy_bracket(
            price=entry_price,
            size=size,
            stopprice=self.stop_loss,
            limitprice=self.take_profit,
            exectype=bt.Order.StopLimit
        )

    def _execute_consolidation_entry(self, size: float, current_price: float):
        """Execute consolidation entry"""
        atr = self.hourly_atr[0]
        
        # Entry at middle of range
        entry_price = (self.hourly.high[0] + self.hourly.low[0]) / 2
        
        # Stop loss below range
        self.stop_loss = self.hourly.low[0] - atr * 0.3
        
        # Take profit at Bollinger top
        self.take_profit = self.daily_boll.lines.top[0]
        
        # Execute bracket order
        self.buy_bracket(
            price=entry_price,
            size=size,
            stopprice=self.stop_loss,
            limitprice=self.take_profit,
            exectype=bt.Order.StopLimit
        )

    def monitor_exit(self):
        """Monitor exit conditions and manage position"""
        try:
            if self.position.size > 0:
                # Dynamic trailing stop
                atr = self.hourly_atr[0]
                trail_price = self.hourly.close[0] - atr * 0.5
                
                # Update stop loss if price moves favorably
                if trail_price > self.stop_loss:
                    self.stop_loss = trail_price
                    logger.debug(f"Stop loss updated to {self.stop_loss}")
                    
        except Exception as e:
            logger.error(f"Error monitoring exit: {e}")

    def notify_order(self, order):
        """Handle order notifications"""
        if order.status in [order.Completed]:
            if order.isbuy():
                logger.info(f"BUY EXECUTED: Price {order.executed.price}, Size {order.executed.size}")
            else:
                logger.info(f"SELL EXECUTED: Price {order.executed.price}, Size {order.executed.size}")
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            logger.warning(f"Order {order.getstatusname()}: {order}")

    def notify_trade(self, trade):
        """Handle trade notifications"""
        if trade.isclosed:
            logger.info(f"Trade P&L: {trade.pnl:.2f}, Commission: {trade.commission:.2f}")

    def get_strategy_info(self) -> Dict[str, Any]:
        """Get strategy information and current state"""
        return {
            'strategy_name': 'ThreeStepStrategy',
            'trend_type': self.trend_type,
            'entry_price': self.entry_price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'trade_count': self.trade_count,
            'position_size': self.position.size if self.position else 0,
            'parameters': {
                'trend_period': self.p.trend_period,
                'entry_period': self.p.entry_period,
                'atr_period': self.p.atr_period,
                'risk_ratio': self.p.risk_ratio
            }
        }
