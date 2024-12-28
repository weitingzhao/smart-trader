

from numpy.f2py.crackfortran import analyzeargs

from logics.logic import Logic
from django.shortcuts import render
from apps.common.models import *
from django.http import JsonResponse
from apps.tasks.controller import Cerebro_task as cerebro

from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models import ColumnDataSource
from jinja2 import Environment, PackageLoader
from backtrader_plotting.bokeh import utils

instance = Logic()

from bokeh.embed import file_html
from bokeh.resources import CDN
from bokeh.document import Document
from backtrader_plotting import Bokeh, OptBrowser, OptComponents

from bokeh.embed import server_document

from bokeh.server.server import Server
from tornado.ioloop import IOLoop

# Global variable to keep track of the server state
# bokeh_server = None

def default(request, symbol, cut_over):
    user_id = request.user.id  # Assuming you have the user_id from the request

    # Step 0. Get default portfolio
    portfolio = Portfolio.objects.filter(user=user_id, is_default=True).order_by('-portfolio_id').first()
    if not portfolio:
        return JsonResponse({'success': False, 'error': 'Default portfolio not found'}, status=404)

    if not symbol:
        return JsonResponse({'success': False, 'error': 'Symbol not provided'}, status=400)

    # Step 1. Run the default strategy
    analysis_result, plot  =  cerebro.run_cerebro_strategy(symbol, cut_over)

    # # Step 2. Optimize the default strategy
    # bokeh, results = cerebro.opt_cerebro_strategy(symbol, cut_over)
    #
    # doc = Document()
    # doc.title = "Backtrader Optimization Result"
    # html_template = "smart_trader.html.j2"
    # scheme = bokeh.params.scheme
    #
    # # set document template
    # env = Environment(loader=PackageLoader('backtrader_plotting.bokeh', 'templates'))
    # doc.template = env.get_template(html_template)
    # doc.template_variables['stylesheet'] = utils.generate_stylesheet(scheme)

    def modify_doc(doc):
        opt_components = OptComponents(bokeh, results)
        model, selector_cds = opt_components.build_optresult_model()
        doc.add_root(model)

    # global bokeh_server
    # if bokeh_server is None:
    #     io_loop = IOLoop.current()
    #     bokeh_server = server = Server({'/bkapp': modify_doc}, io_loop=io_loop, allow_websocket_origin=["localhost:8108"])
    #     bokeh_server = server.start()
    # script = server_document('http://localhost:8108/bkapp')

    return render(
        request=request,
        template_name='pages/analytics/risk_analysis.html',
        context= {
            'parent': 'analytics',
            'segment': 'risk_analysis',
            # 'analysis_result': analysis_result,
            'plot': plot,

            # 'bokeh_script': bokeh_script,
            # 'plot_script': script,
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