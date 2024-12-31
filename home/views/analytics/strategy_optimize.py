import os
import pickle
from django.shortcuts import render

from apps.bokeh.views import with_url_args
from apps.common.models import *
from django.http import JsonResponse

from backtrader_plotting import Bokeh, OptBrowser
from backtrader_plotting.schemes import Tradimo
from cerebro.strategy_optimize import StrategyOptimize
from bokeh.client import pull_session
from bokeh.embed import server_session
from bokeh.document import Document
import param
from bokeh.plotting import figure
import numpy as np
import panel as pn

from typing import Any
from bokeh.embed import server_document
from bokeh.io import curdoc
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Slider
from bokeh.plotting import figure
from os.path import join
from django.conf import settings
from bokeh.sampledata.sea_surface_temperature import sea_surface_temperature


from bokeh.themes import Theme

from home.views.analytics.market_comparison import ray_sample_pi, ray_strategy_optimize

theme = Theme(filename=join(settings.THEMES_DIR, "theme.yaml"))


def default(request, symbol, cut_over):
    user_id = request.user.id  # Assuming you have the user_id from the request

    # Step 0. Get default portfolio
    portfolio = Portfolio.objects.filter(user=user_id, is_default=True).order_by('-portfolio_id').first()
    if not portfolio:
        return JsonResponse({'success': False, 'error': 'Default portfolio not found'}, status=404)

    # sample
    script = server_document(request.get_full_path())

    return render(
        request=request,
        template_name='pages/analytics/strategy_optimize.html',
        context= {
            'parent': 'analytics',
            'segment': 'strategy_optimize',
            'script': script,
        })

@with_url_args
def bokeh_optimize(doc: Document, symbol, cut_over) -> None:

    # pi = ray_sample_pi()
    doc.theme = theme

    results = ray_strategy_optimize(symbol, cut_over)

    # get strategy optimize request Assign the model to the global variable
    bokeh = Bokeh(style='bar', scheme=Tradimo(), output_mode='memory')
    browser = OptBrowser(bokeh, results)
    model = browser.build_optresult_model()
    doc.add_root(model)


def prepare_plot():
    df = sea_surface_temperature.copy()
    source = ColumnDataSource(data=df)

    plot = figure(x_axis_type="datetime", y_range=(0, 25), y_axis_label="Temperature (Celsius)",
                  title="Sea Surface Temperature at 43.18, -70.43")
    plot.line("time", "temperature", source=source)

    def callback(attr: str, old: Any, new: Any) -> None:
        if new == 0:
            data = df
        else:
            data = df.rolling(f"{new}D").mean()
        source.data = dict(ColumnDataSource(data=data).data)

    slider = Slider(start=0, end=30, value=0, step=1, title="Smoothing by N Days")
    slider.on_change("value", callback)

    return slider, plot

def shape_viewer():
    shapes = [NGon(), Circle()]
    viewer = ShapeViewer()
    viewer.param.shape.objects = shapes
    viewer.shape = shapes[0]
    return viewer.panel()


class Shape(param.Parameterized):

    radius = param.Number(default=1, bounds=(0, 1))

    def __init__(self, **params) -> None:
        super().__init__(**params)
        self.figure = figure(x_range=(-1, 1), y_range=(-1, 1))
        self.renderer = self.figure.line(*self._get_coords())

    def _get_coords(self):
        return [], []

    def view(self):
        return self.figure


class Circle(Shape):

    n = param.Integer(default=100, precedence=-1)

    def __init__(self, **params) -> None:
        super().__init__(**params)

    def _get_coords(self):
        angles = np.linspace(0, 2*np.pi, self.n+1)
        return (self.radius*np.sin(angles),
                self.radius*np.cos(angles))

    @param.depends('radius', watch=True)
    def update(self):
        xs, ys = self._get_coords()
        self.renderer.data_source.data.update({'x': xs, 'y': ys})


class NGon(Circle):

    n = param.Integer(default=3, bounds=(3, 10), precedence=1)

    @param.depends('radius', 'n', watch=True)
    def update(self):
        xs, ys = self._get_coords()
        self.renderer.data_source.data.update({'x': xs, 'y': ys})


shapes = [NGon(), Circle()]


class ShapeViewer(param.Parameterized):

    shape = param.ObjectSelector(default=shapes[0], objects=shapes)

    @param.depends('shape')
    def view(self):
        return self.shape.view()

    @param.depends('shape', 'shape.radius')
    def title(self):
        return '## %s (radius=%.1f)' % (type(self.shape).__name__, self.shape.radius)

    def panel(self):
        expand_layout = pn.Column()

        return pn.Column(
            pn.pane.HTML('<h1>Bokeh Integration Example using Param and Panel</h1>'),
            pn.widgets.Tabulator(),
            pn.Row(
                pn.Column(
                    pn.panel(self.param, expand_button=False, expand=True, expand_layout=expand_layout),
                    "#### Subobject parameters:",
                    expand_layout),
                pn.Column(self.title, self.view)
            ),
            sizing_mode='stretch_width',
        )









