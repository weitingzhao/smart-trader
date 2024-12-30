from os.path import join
from typing import Any
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from bokeh.document import Document
from bokeh.embed import server_document
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, Slider
from bokeh.plotting import figure
from bokeh.sampledata.sea_surface_temperature import sea_surface_temperature
from bokeh.themes import Theme
import panel as pn
import inspect

from .shape_viewer import shape_viewer

theme = Theme(filename=join(settings.THEMES_DIR, "theme.yaml"))


def _get_args_kwargs_from_doc(doc):
    request = doc.session_context.request
    args = request.url_route['args']
    kwargs = request.url_route['kwargs']
    return args, kwargs

def with_url_args(handler):
    # Note that functools.wraps cannot be used here because Bokeh requires that the signature of the returned function
    # must only accept single (Document) argument
    def wrapper(doc):
        args, kwargs = _get_args_kwargs_from_doc(doc)
        return handler(doc, *args, **kwargs)

    async def async_wrapper(doc):
        args, kwargs = _get_args_kwargs_from_doc(doc)
        return await handler(doc, *args, **kwargs)

    return async_wrapper if inspect.iscoroutinefunction(handler) else wrapper


def index(request: HttpRequest) -> HttpResponse:
    return render(
        request=request, template_name='pages/bokeh/index.html',
        context={})

def shapes(request: HttpRequest) -> HttpResponse:
    script = server_document(request.get_full_path())
    return render(
        request=request,
        template_name="pages/bokeh/embed.html",
        context= dict(script=script))

def shapes_with_args(request: HttpRequest, arg1: str, arg2: str) -> HttpResponse:
    script = server_document(request.get_full_path())
    return render(
        request=request,
        template_name="pages/bokeh/embed.html",
        context=dict(script=script))

def shape_viewer_handler(doc: Document) -> None:
    panel = shape_viewer()
    panel.server_doc(doc)


@with_url_args
async def shape_viewer_handler_with_args(doc, arg1, arg2):
    viewer = shape_viewer()
    pn.Column(
        viewer,
        pn.pane.Markdown(f'## This app has URL Args: {arg1} and {arg2}')
    ).server_doc(doc)
