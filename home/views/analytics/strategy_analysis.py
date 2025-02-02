import json
import base64
from django.shortcuts import render
from apps.common.models import *
from django.http import JsonResponse
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import ColumnDataSource
from bokeh.embed import server_document
from bokeh.document import Document
from apps.tasks.controller.instance import Instance
from cerebro.ray_strategy import RayStrategyProfile

from cerebro.strategy.strategy1stoperation import Strategy1stOperation
from home.templatetags.request_url import with_url_args

instance = Instance()

def default(request, data:str = None):
    user_id = request.user.id  # Assuming you have the user_id from the request
    # basic check
    portfolio = Portfolio.objects.filter(user=user_id, is_default=True).order_by('-portfolio_id').first()
    if not portfolio:
        return JsonResponse({'success': False, 'error': 'Default portfolio not found'}, status=404)

    return render(
        request=request,
        template_name='pages/analytics/strategy_analysis.html',
        context= {
            'parent': 'analytics',
            'segment': 'strategy_analysis',
        })


def backtrader_plot(request, data:str = None):
    user_id = request.user.id  # Assuming you have the user_id from the request
    # Step 0. Get default portfolio
    portfolio = Portfolio.objects.filter(user=user_id, is_default=True).order_by('-portfolio_id').first()
    if not portfolio:
        return JsonResponse({'success': False, 'error': 'Default portfolio not found'}, status=404)

    script = server_document(request.get_full_path())

    # for display purpose
    decoded_data = base64.b64decode(data).decode('utf-8')
    data_json = json.loads(decoded_data)

    return render(
        request=request,
        template_name='pages/analytics/strategy_analysis_plot.html',
        context= {
            'script':script,
            'data_json': data_json,
        })

@with_url_args
def test_result(doc: Document, data) -> None:
    if  data is None:
        return
    decoded_data = base64.b64decode(data).decode('utf-8')
    data_json = json.loads(decoded_data)

    # Step 1. Convert the QuerySet to a DataFrame
    strategyProfile = RayStrategyProfile(stdstats=True)
    # Step 2. Set Data
    strategyProfile.set_data(data_json = data_json)
    # Step 3. Load Startegy
    strategyProfile.set_strategy(Strategy1stOperation)
    # Step 4. Run the strategy
    strategyProfile.run()
    # Step 5. Plot the strategy
    analysis_result, model = strategyProfile.plot()
    doc.add_root(model)


def ray_strategy_optimize(symbol, cut_over):

    # Prepare the JSON object with parameters
    data_json = json.dumps({
        'symbols': symbol,
        'period': 'max',  # Example period, replace with actual value if needed
        'interval': '60m',  # Example interval, replace with actual value if needed
        'since': cut_over
    })

    # Step 1. Convert the QuerySet to a DataFrame
    strategyProfile = RayStrategyProfile(stdstats=True)
    # Step 2. Set Data
    strategyProfile.set_data(data_json = data_json)
    # Step 3. Load Startegy
    # file_content = StrategyAlgoScript.objects.filter(name='default_strategy.py').first()
    # strategyProfile.set_strategy(file_content.content)
    strategyProfile.set_strategy(Strategy1stOperation)
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