from cerebro.strategy_profile import StrategyProfile
from logics.logic import Logic
from django.shortcuts import render
from apps.common.models import *
from django.http import JsonResponse

from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import ColumnDataSource

instance = Logic()

def default(request, symbol, cut_over):
    user_id = request.user.id  # Assuming you have the user_id from the request

    # Step 0. Get default portfolio
    portfolio = Portfolio.objects.filter(user=user_id, is_default=True).order_by('-portfolio_id').first()
    if not portfolio:
        return JsonResponse({'success': False, 'error': 'Default portfolio not found'}, status=404)

    if not symbol:
        return JsonResponse({'success': False, 'error': 'Symbol not provided'}, status=400)

    # Part A. Run the default strategy
    analysis_result, plot = StrategyProfile().run(symbol, cut_over)

    return render(
        request=request,
        template_name='pages/analytics/strategy_analysis.html',
        context= {
            'parent': 'analytics',
            'segment': 'strategy_analysis',
            'analysis_result': analysis_result,
            'plot': plot,
        })


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