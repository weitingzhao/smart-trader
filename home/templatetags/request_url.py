import inspect
import numpy as np
from decimal import Decimal


def _get_args_kwargs_from_doc(doc):
    request = doc.session_context.request
    args = request.url_route['args']
    kwargs = request.url_route['kwargs']
    return args, kwargs


def with_request(handler):
    # Note that functools.wraps cannot be used here because Bokeh requires that the signature of the returned function
    # must only accept single (Document) argument
    def wrapper(doc):
        return handler(doc, doc.session_context.request)
    async def async_wrapper(doc):
        return await handler(doc, doc.session_context.request)
    return async_wrapper if inspect.iscoroutinefunction(handler) else wrapper

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

# Convert Decimal and int64 values to standard Python types
def convert_to_serializable(data):
    if isinstance(data, dict):
        return {k: convert_to_serializable(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_to_serializable(i) for i in data]
    elif isinstance(data, Decimal):
        return float(data)
    elif isinstance(data, np.int64):
        return int(data)
    else:
        return data