from runpy import run_module

import pandas as pd

from cerebro.ray_strategy import RayStrategyProfile
from django.shortcuts import render
from apps.common.models import *
from django.http import JsonResponse
import ray
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import ColumnDataSource

from cerebro.strategy.test_strategy_1st import TestStrategy


def default(request, symbol, cut_over):
    user_id = request.user.id  # Assuming you have the user_id from the request

    # Step 0. Get default portfolio
    portfolio = Portfolio.objects.filter(user=user_id, is_default=True).order_by('-portfolio_id').first()
    if not portfolio:
        return JsonResponse({'success': False, 'error': 'Default portfolio not found'}, status=404)

    if not symbol:
        return JsonResponse({'success': False, 'error': 'Symbol not provided'}, status=400)

    analysis_result, plot = ray_strategy_optimize(symbol, cut_over)

    return render(
        request=request,
        template_name='pages/analytics/strategy_analysis.html',
        context= {
            'parent': 'analytics',
            'segment': 'strategy_analysis',
            'analysis_result': analysis_result,
            'plot': plot,
        })

def ray_strategy_optimize(symbol, cut_over):
    # Step 1.  Prepare data as Data Frame
    stock_data = (MarketStockHistoricalBarsByDay.objects
                  .filter(symbol=symbol, time__gte=cut_over).order_by('time'))
    stock_data_df = pd.DataFrame(list(stock_data.values()))

    return run_by_normal(symbol, cut_over, stock_data_df)
    # return run_by_ray(symbol, cut_over,stock_data_df)


def run_by_normal(symbol, cut_over, stock_data_df):
    # Step 2. Convert the QuerySet to a DataFrame
    strategyProfile = RayStrategyProfile(stdstats=False)
    strategyProfile.set_data(data_name=f'{symbol}-{cut_over}', data_df=stock_data_df)

    # Step 3. Load Startegy
    # file_content = StrategyAlgoScript.objects.filter(name='default_strategy.py').first()
    # strategyProfile.set_strategy(file_content.content)
    strategyProfile.set_strategy(TestStrategy)

    # Step 4. Run the strategy
    strategyProfile.run()

    # Step 5. Plot the strategy
    return strategyProfile.plot()

# def run_by_ray(symbol, cut_over, stock_data_df):
#
#     # Step 2. Convert the QuerySet to a DataFrame
#     strategyProfile = RayStrategyProfile.remote(stdstats=False)
#     strategyProfile.set_data.remote(data_name=f'{symbol}-{cut_over}', data_df=stock_data_df)
#
#     # Step 3. Load Startegy
#     file_content = StrategyAlgoScript.objects.filter(name='default_strategy.py').first()
#     strategyProfile.set_strategy.remote(file_content.content)
#
#     # Step 4. Run the strategy
#     strategyProfile.run.remote()
#
#     # Step 5. Plot the strategy
#     return ray.get(strategyProfile.plot.remote())


def create_sample_bokeh_chart():
    # Create some data
    data = {'x': [1, 2, 3, 4, 5], 'y': [6, 7, 2, 4, 5]}
    source = ColumnDataSource(data=data)

    # Create a figure
    p = figure(title="Static Bokeh Chart", x_axis_label="X-Axis", y_axis_label="Y-Axis", tools="pan, box_zoom, reset, save")

    # Add a line plot
    p.line('x', 'y', source=source, line_width=2)

    # Embed the chart
    script, div = components(p)
    return script, div