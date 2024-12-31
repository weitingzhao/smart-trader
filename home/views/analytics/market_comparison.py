import time

import pandas as pd
import ray
from django.shortcuts import render

from cerebro.ray_actor import StrategyOptimizeRay
from cerebro.ray_sample_pi import ProgressActor, sampling_task
from apps.common.models import *

def default(request):
    symbol = 'DAVE'
    cut_over = '2024-05-01'

    res = ray_strategy_optimize(symbol, cut_over)


    return render(
        request=request,
        template_name='pages/analytics/market_comparison.html',
        context= {
            'parent': 'analytics',
            'segment': 'market_comparison',
            'result': res
        })

def ray_strategy_optimize(symbol, cut_over):

    stock_data = (MarketStockHistoricalBarsByDay.objects
                  .filter(symbol=symbol, time__gte=cut_over).order_by('time'))
    stock_data_df = pd.DataFrame(list(stock_data.values()))

    # Convert the QuerySet to a DataFrame
    strategyOptimize = StrategyOptimizeRay.remote()
    res = ray.get(strategyOptimize.run.remote(symbol, cut_over, stock_data_df))
    return res

def ray_sample_pi():
    # Change this to match your cluster scale.
    NUM_SAMPLING_TASKS = 10
    NUM_SAMPLES_PER_TASK = 10_000_000
    TOTAL_NUM_SAMPLES = NUM_SAMPLING_TASKS * NUM_SAMPLES_PER_TASK

    # Create the progress actor.
    progress_actor = ProgressActor.remote(TOTAL_NUM_SAMPLES)

    # Create and execute all sampling tasks in parallel.
    results = [
        sampling_task.remote(NUM_SAMPLES_PER_TASK, i, progress_actor)
        for i in range(NUM_SAMPLING_TASKS)
    ]

    # Query progress periodically.
    while True:
        progress = ray.get(progress_actor.get_progress.remote())
        print(f"Progress: {int(progress * 100)}%")

        if progress == 1:
            break
        time.sleep(1)

    # Get all the sampling tasks results.
    total_num_inside = sum(ray.get(results))
    pi = (total_num_inside * 4) / TOTAL_NUM_SAMPLES
    print(f"Estimated value of π is: {pi}")

    return pi