import ray
import backtrader as bt
from typing import Dict, Any, List, Tuple
import logging
from concurrent.futures import ThreadPoolExecutor
import asyncio

logger = logging.getLogger(__name__)

@ray.remote
class RayStrategyOptimizer:
    """Ray-based strategy optimizer for distributed computing"""
    
    def __init__(self):
        self.optimization_results = {}
    
    def optimize_strategy(self, strategy_class, data_config: Dict[str, Any], 
                         parameter_ranges: Dict[str, List[float]], 
                         optimization_type: str = "parameter") -> Dict[str, Any]:
        """Optimize strategy parameters using Ray"""
        try:
            logger.info(f"Starting optimization for {strategy_class.__name__}")
            
            if optimization_type == "parameter":
                return self._parameter_optimization(strategy_class, data_config, parameter_ranges)
            elif optimization_type == "walk_forward":
                return self._walk_forward_optimization(strategy_class, data_config, parameter_ranges)
            else:
                raise ValueError(f"Unknown optimization type: {optimization_type}")
                
        except Exception as e:
            logger.error(f"Error in optimization: {e}")
            return {"error": str(e)}
    
    def _parameter_optimization(self, strategy_class, data_config: Dict[str, Any], 
                               parameter_ranges: Dict[str, List[float]]) -> Dict[str, Any]:
        """Parameter optimization using grid search"""
        try:
            # Generate parameter combinations
            param_combinations = self._generate_parameter_combinations(parameter_ranges)
            
            # Run backtests for each combination
            results = []
            for params in param_combinations:
                result = self._run_single_backtest(strategy_class, data_config, params)
                if result:
                    results.append(result)
            
            # Find best parameters
            if results:
                best_result = max(results, key=lambda x: x.get('total_return', 0))
                return {
                    "best_parameters": best_result['parameters'],
                    "best_performance": {
                        "total_return": best_result['total_return'],
                        "sharpe_ratio": best_result.get('sharpe_ratio', 0),
                        "max_drawdown": best_result.get('max_drawdown', 0)
                    },
                    "all_results": results,
                    "optimization_type": "parameter"
                }
            else:
                return {"error": "No valid results found"}
                
        except Exception as e:
            logger.error(f"Error in parameter optimization: {e}")
            return {"error": str(e)}
    
    def _walk_forward_optimization(self, strategy_class, data_config: Dict[str, Any], 
                                  parameter_ranges: Dict[str, List[float]]) -> Dict[str, Any]:
        """Walk-forward optimization"""
        try:
            # This would implement walk-forward analysis
            # For now, return a placeholder
            return {
                "message": "Walk-forward optimization not yet implemented",
                "optimization_type": "walk_forward"
            }
            
        except Exception as e:
            logger.error(f"Error in walk-forward optimization: {e}")
            return {"error": str(e)}
    
    def _generate_parameter_combinations(self, parameter_ranges: Dict[str, List[float]]) -> List[Dict[str, float]]:
        """Generate all parameter combinations"""
        import itertools
        
        # Get parameter names and values
        param_names = list(parameter_ranges.keys())
        param_values = list(parameter_ranges.values())
        
        # Generate all combinations
        combinations = list(itertools.product(*param_values))
        
        # Convert to list of dictionaries
        param_combinations = []
        for combo in combinations:
            param_dict = dict(zip(param_names, combo))
            param_combinations.append(param_dict)
        
        logger.info(f"Generated {len(param_combinations)} parameter combinations")
        return param_combinations
    
    def _run_single_backtest(self, strategy_class, data_config: Dict[str, Any], 
                           parameters: Dict[str, float]) -> Dict[str, Any]:
        """Run a single backtest with given parameters"""
        try:
            # Import here to avoid circular imports
            from ..backtesting.cerebro_base import CerebroBase
            
            # Create Cerebro instance
            cerebro = CerebroBase()
            
            # Set data
            success = cerebro.set_data_from_yahoo(
                symbols=data_config['symbol'],
                period=data_config.get('period', '1y'),
                since=data_config.get('start_date')
            )
            
            if not success:
                return None
            
            # Set strategy with parameters
            cerebro.set_strategy(strategy_class, **parameters)
            
            # Run backtest
            results = cerebro.run_backtest()
            
            # Add parameters to results
            results['parameters'] = parameters
            
            return results
            
        except Exception as e:
            logger.error(f"Error running single backtest: {e}")
            return None

class StrategyOptimizationService:
    """Service for strategy optimization"""
    
    def __init__(self):
        self.ray_optimizer = None
        self.optimization_tasks = {}
    
    async def initialize_ray(self):
        """Initialize Ray for distributed computing"""
        try:
            if not ray.is_initialized():
                ray.init(ignore_reinit_error=True)
            
            # Create Ray optimizer
            self.ray_optimizer = RayStrategyOptimizer.remote()
            logger.info("Ray optimizer initialized")
            
        except Exception as e:
            logger.error(f"Error initializing Ray: {e}")
            raise
    
    async def optimize_strategy_async(self, strategy_class, data_config: Dict[str, Any], 
                                     parameter_ranges: Dict[str, List[float]], 
                                     optimization_type: str = "parameter") -> Dict[str, Any]:
        """Run strategy optimization asynchronously"""
        try:
            if not self.ray_optimizer:
                await self.initialize_ray()
            
            # Run optimization on Ray
            optimization_task = self.ray_optimizer.optimize_strategy.remote(
                strategy_class, data_config, parameter_ranges, optimization_type
            )
            
            # Wait for result
            result = await optimization_task
            
            return result
            
        except Exception as e:
            logger.error(f"Error in async optimization: {e}")
            return {"error": str(e)}
    
    def optimize_strategy_sync(self, strategy_class, data_config: Dict[str, Any], 
                              parameter_ranges: Dict[str, List[float]], 
                              optimization_type: str = "parameter") -> Dict[str, Any]:
        """Run strategy optimization synchronously"""
        try:
            # Use ThreadPoolExecutor for sync execution
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(
                    self._run_optimization_sync,
                    strategy_class, data_config, parameter_ranges, optimization_type
                )
                return future.result()
                
        except Exception as e:
            logger.error(f"Error in sync optimization: {e}")
            return {"error": str(e)}
    
    def _run_optimization_sync(self, strategy_class, data_config: Dict[str, Any], 
                              parameter_ranges: Dict[str, List[float]], 
                              optimization_type: str) -> Dict[str, Any]:
        """Run optimization synchronously"""
        try:
            # Initialize Ray if not already done
            if not ray.is_initialized():
                ray.init(ignore_reinit_error=True)
            
            # Create optimizer
            optimizer = RayStrategyOptimizer.remote()
            
            # Run optimization
            result = ray.get(optimizer.optimize_strategy.remote(
                strategy_class, data_config, parameter_ranges, optimization_type
            ))
            
            return result
            
        except Exception as e:
            logger.error(f"Error in sync optimization execution: {e}")
            return {"error": str(e)}
    
    def get_optimization_status(self, optimization_id: str) -> Dict[str, Any]:
        """Get optimization status"""
        try:
            # This would check the status of running optimizations
            return {
                "optimization_id": optimization_id,
                "status": "completed",
                "progress": 100
            }
            
        except Exception as e:
            logger.error(f"Error getting optimization status: {e}")
            return {"error": str(e)}
    
    def stop_optimization(self, optimization_id: str) -> bool:
        """Stop running optimization"""
        try:
            # This would stop the optimization task
            if optimization_id in self.optimization_tasks:
                del self.optimization_tasks[optimization_id]
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error stopping optimization: {e}")
            return False

# Global optimization service instance
optimization_service = StrategyOptimizationService()
