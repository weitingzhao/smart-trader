import redis
import pandas as pd
import backtrader as bt
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class CerebroBase:
    """Refactored Cerebro base class for Strategy Service"""
    
    def __init__(self, stdstats=False):
        # Create a cerebro entity
        self.cerebro = bt.Cerebro(stdstats=stdstats)
        self.data_condition = None
        self.data_name = None
        self.data = None
        self.data_df = None
        self.result = None
        self.strategy = None
        
        # Redis connection
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        self.redis_client = redis.from_url(redis_url)
        
        # Configuration
        self.sms_need = False
        self.msg_group_name = 'stock_bt_result'
        
        # Data service URL for fetching data
        self.data_service_url = os.getenv('DATA_SERVICE_URL', 'http://data-service:8000')
        
        logger.info("CerebroBase initialized")

    def set_data_from_service(self, symbols: str, period: str = "1y", 
                            interval: str = "1d", since: str = None) -> bool:
        """Set data from data service instead of direct Yahoo Finance"""
        try:
            import httpx
            
            # Prepare data request
            data_request = {
                'symbols': symbols,
                'period': period,
                'interval': interval,
                'since': since or (datetime.now().replace(year=datetime.now().year-1)).strftime('%Y-%m-%d')
            }
            
            # Fetch data from data service
            with httpx.Client() as client:
                response = client.get(f"{self.data_service_url}/api/market/historical/{symbols}")
                if response.status_code == 200:
                    data = response.json()
                    self._process_data(data, symbols, since)
                    return True
                else:
                    logger.error(f"Failed to fetch data: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error fetching data from service: {e}")
            return False

    def set_data_from_yahoo(self, symbols: str, period: str = "1y", 
                           interval: str = "1d", since: str = None) -> bool:
        """Set data directly from Yahoo Finance (fallback method)"""
        try:
            import yfinance as yf
            
            # Extract symbols
            symbol_list = symbols.split('|') if '|' in symbols else [symbols]
            since_date = since or (datetime.now().replace(year=datetime.now().year-1)).strftime('%Y-%m-%d')
            
            # Fetch data for each symbol
            all_data = {}
            for symbol in symbol_list:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period=period, interval=interval)
                
                if not data.empty:
                    # Filter by since date
                    data = data[data.index >= since_date]
                    all_data[symbol] = data
            
            if all_data:
                # Use first symbol's data for now (can be extended for multi-symbol)
                first_symbol = list(all_data.keys())[0]
                self._process_data(all_data[first_symbol], first_symbol, since_date)
                return True
            else:
                logger.error("No data retrieved from Yahoo Finance")
                return False
                
        except Exception as e:
            logger.error(f"Error fetching data from Yahoo Finance: {e}")
            return False

    def _process_data(self, data: pd.DataFrame, symbols: str, since: str):
        """Process and prepare data for Backtrader"""
        try:
            # Ensure data is a DataFrame
            if not isinstance(data, pd.DataFrame):
                data = pd.DataFrame(data)
            
            # Rename columns to match Backtrader format
            data.rename(columns={
                'Open': 'open',
                'High': 'high', 
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume',
            }, inplace=True)
            
            # Remove unnecessary columns
            columns_to_drop = ['Dividends', 'Stock Splits']
            for col in columns_to_drop:
                if col in data.columns:
                    data.drop(columns=[col], inplace=True)
            
            # Set datetime index
            data.rename_axis('datetime', inplace=True)
            
            # Add openinterest column
            data['openinterest'] = 0
            
            # Store processed data
            self.data_name = f'{symbols}-{since}'
            self.data_df = data
            
            # Store data condition
            self.data_condition = {
                'symbols': symbols,
                'period': '1y',
                'interval': '1d', 
                'since': since
            }
            
            logger.info(f"Data processed successfully for {symbols}")
            
        except Exception as e:
            logger.error(f"Error processing data: {e}")
            raise

    def _prepare_data(self):
        """Add the Data Feed to Cerebro"""
        if self.data_df is None:
            raise ValueError("No data available. Call set_data_from_service() or set_data_from_yahoo() first.")
        
        # Add the Data Feed to Cerebro
        self.data = bt.feeds.PandasData(dataname=self.data_df)
        self.data._name = self.data_name
        self.cerebro.adddata(self.data)
        
        logger.info(f"Data prepared for Cerebro: {self.data_name}")

    def set_strategy(self, strategy_class, **params):
        """Set strategy with parameters"""
        self.strategy = strategy_class
        self.strategy_params = params
        logger.info(f"Strategy set: {strategy_class.__name__}")

    def configure(self, initial_cash: float = 10000.0, commission: float = 0.001, 
                 stake_size: int = 10):
        """Configure Cerebro with trading parameters"""
        # Set initial cash
        self.cerebro.broker.setcash(initial_cash)
        
        # Add sizer
        self.cerebro.addsizer(bt.sizers.FixedSize, stake=stake_size)
        
        # Set commission
        self.cerebro.broker.setcommission(commission=commission)
        
        # Add analyzers
        self.cerebro.addanalyzer(bt.analyzers.SQN)
        self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer)
        self.cerebro.addanalyzer(bt.analyzers.SharpeRatio)
        self.cerebro.addanalyzer(bt.analyzers.DrawDown)
        self.cerebro.addanalyzer(bt.analyzers.Returns)
        
        # Add observers
        self.cerebro.addobserver(bt.observers.DrawDown)
        self.cerebro.addobserver(bt.observers.Broker)
        
        logger.info("Cerebro configured successfully")

    def run_backtest(self) -> Dict[str, Any]:
        """Run backtest and return results"""
        try:
            # Prepare data
            self._prepare_data()
            
            # Configure
            self.configure()
            
            # Add strategy with parameters
            if self.strategy_params:
                self.cerebro.addstrategy(self.strategy, **self.strategy_params)
            else:
                self.cerebro.addstrategy(self.strategy)
            
            # Run backtest
            self.result = self.cerebro.run(optreturn=True)
            
            # Extract results
            results = self._extract_results()
            
            # Send message if needed
            if self.sms_need:
                self._send_message()
            
            logger.info("Backtest completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Error running backtest: {e}")
            raise

    def _extract_results(self) -> Dict[str, Any]:
        """Extract results from backtest"""
        if not self.result:
            return {}
        
        st0 = self.result[0]
        
        # Extract basic metrics
        results = {
            'initial_cash': self.cerebro.broker.startingcash,
            'final_cash': self.cerebro.broker.getvalue(),
            'total_return': (self.cerebro.broker.getvalue() - self.cerebro.broker.startingcash) / self.cerebro.broker.startingcash,
            'data_condition': self.data_condition,
            'strategy': self.strategy.__name__ if self.strategy else None
        }
        
        # Extract analyzer results
        for analyzer in st0.analyzers:
            analyzer_name = analyzer.__class__.__name__
            if hasattr(analyzer, 'get_analysis'):
                results[analyzer_name.lower()] = analyzer.get_analysis()
        
        return results

    def _send_message(self):
        """Send results message to Redis"""
        try:
            if not self.result:
                return
            
            st0 = self.result[0]
            
            # Extract indicators if available
            detail = {}
            if hasattr(st0, 'atr'):
                detail['atr'] = st0.atr.array[-1] if hasattr(st0.atr, 'array') else 0
            
            if hasattr(st0, 'bbands'):
                detail['bbands'] = {
                    'upper': st0.bbands.lines.bolu.array[-1] if hasattr(st0.bbands.lines.bolu, 'array') else 0,
                    'middle': st0.bbands.lines.mid.array[-1] if hasattr(st0.bbands.lines.mid, 'array') else 0,
                    'lower': st0.bbands.lines.bold.array[-1] if hasattr(st0.bbands.lines.bold, 'array') else 0
                }
            
            # Prepare message
            message = {
                'type': 'bt_symbol',
                'meta': self.data_condition,
                'indicator': detail,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Send to Redis
            json_str = json.dumps(message)
            self.redis_client.publish(self.msg_group_name, json_str)
            
            logger.info(f"Message sent to Redis: {self.msg_group_name}")
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")

    def get_plot_data(self):
        """Get plot data for visualization"""
        if not self.result:
            return None
        
        try:
            from backtrader_plotting import Bokeh
            from backtrader_plotting.schemes import Tradimo
            
            # Create Bokeh plot
            bokeh = Bokeh(
                style='bar',
                plot_mode='single',
                scheme=Tradimo(),
                output_mode='memory'
            )
            
            # Generate plot
            self.cerebro.plot(bokeh, iplot=False)
            
            return bokeh.figurepages[0].model if bokeh.figurepages else None
            
        except Exception as e:
            logger.error(f"Error generating plot: {e}")
            return None
