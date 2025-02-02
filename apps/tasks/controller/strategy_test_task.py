from typing import List

import pandas as pd

from cerebro.strategy.strategy1stoperation import Strategy1stOperation
from .instance import Instance
from .base_task import BaseTask
from django_celery_results.models import TaskResult
from cerebro.ray_strategy import RayStrategyProfile
from ...common.models import MarketStockHistoricalBarsByDay
import redis

class StrategyTestTask(BaseTask):

    def __init__(self, celery, data):
        super().__init__(celery, data)

    def job_scripts(self) -> List:
        return [
            {"name":"Strategy test DAVE since 2024-05-01"},
            {"name":"Strategy test OWL since 2024-05-01"},
        ]

    def _worker_run(self, script_name: str, instance : Instance, task_result: TaskResult, meta: dict, args: str = None):
        # Step 1.  Get the screening operations
        # self.ray_strategy_optimize('DAVE', '2024-05-01')

        # Push result to Redis
        result = {"x": [1, 2, 3], "y": [4, 5, 6]}  # Example result
        redis_client = redis.StrictRedis(host='localhost', port=6379, db=1)
        redis_client.publish("bokeh_plot_channel", str(result))



    def ray_strategy_optimize(self, symbol, cut_over):
        # Step 1.  Prepare data as Data Frame
        stock_data = (MarketStockHistoricalBarsByDay.objects
                      .filter(symbol=symbol, time__gte=cut_over).order_by('time'))
        stock_data_df = pd.DataFrame(list(stock_data.values()))

        return self.run_by_normal(symbol, cut_over, stock_data_df)

    def run_by_normal(self, symbol, cut_over, stock_data_df):
        # Step 2. Convert the QuerySet to a DataFrame
        strategyProfile = RayStrategyProfile(stdstats=True)
        strategyProfile.set_data(data_name=f'{symbol}-{cut_over}', data_df=stock_data_df)

        # Step 3. Load Startegy
        # file_content = StrategyAlgoScript.objects.filter(name='default_strategy.py').first()
        # strategyProfile.set_strategy(file_content.content)
        strategyProfile.set_strategy(Strategy1stOperation)

        # Step 4. Run the strategy
        strategyProfile.run()

        # Step 5. Plot the strategy
        return strategyProfile.plot()