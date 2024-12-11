import json

from django import template
import random
import string
from datetime import datetime
from apps.common.models import *

register = template.Library()

@register.filter
def yes_no(value, arg):
    return "Yes" if  arg else "No"

@register.filter
def action_lookup(value, arg):
    # Lookup dictionaries
    return dict(ActionChoices.choices).get(arg)

@register.filter
def timing_lookup(value, arg):
    # Lookup dictionaries
    return dict(TimingChoices.choices).get(arg)

@register.filter
def funding_lookup(value, arg):
    # Lookup dictionaries
    return dict(FundingTypeChoices.choices).get(arg)

@register.filter
def transaction_type_lookup(value, arg):
    # Lookup dictionaries
    return dict(TransactionTypeChoices.choices).get(arg)

@register.filter(name='replace_value')
def replace_value(value, arg):
    """Removes all values of arg from the given string"""
    return value.replace(arg, ' ').title()

@register.filter
def to_json(value):
    """Converts a JSON string to a JSON object"""
    try:
        return json.loads(value)
    except (ValueError, TypeError):
        return {}

@register.filter
def order_name(value, order):
    price = order_price(None, order)
    return f"{order.quantity_target} @ {price}"

@register.filter
def order_price(value, order):
    if order.order_type == '1': #market
        return f"{order.price_market} Market"
    elif order.order_type == '2':  # limit
        return f"{order.price_limt} Limit"
    elif order.order_type == '3':  # limit
        return f"{order.price_stop} Stop"
    elif order.order_type == '4': #stop limit
        return f"{order.price_stop} / {order.price_limit} Stop Limit"
    else:
        return f""

@register.filter
def format_date(value, date_format):
    """Parses a date string and formats it according to the given parameter."""
    try:
        # Remove the 'Z' character if present
        if value.endswith('Z'):
            value = value[:-1]
        date_obj = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
        return date_obj.strftime(date_format)
    except:
        return value

@register.simple_tag
def trade_phase_fa_icon(value, is_class=False):
    if value == TradePhaseChoices.BEFORE_BO:
        return 'fas fa-hourglass-end fa-sm' if is_class else 'color:black'
    elif value == TradePhaseChoices.BREAKING:
        return 'fas fa-hourglass-half fa-sm' if is_class else 'color:#8c0404'
    elif value == TradePhaseChoices.AFTER_BO:
        return 'fas fa-hourglass-start fa-sm' if is_class else 'color:#8fda2d'
    else:
        return 'fas fa-stop fa-sm' if is_class else 'color:grey'

@register.simple_tag
def round_by_digits(value, digits, template :str, need_plus=True):
    """Rounds the value to the given number of digits"""
    if value is None:
        return '-'
    try:
        value = float(value)
        digits = int(digits)
        rounded_value = round(value, digits)
        rounded_str = f"{rounded_value:,.{digits}f}"
        if need_plus and value > 0:
            rounded_str = f"+{rounded_str}"
        if template:
            return template.format(rounded_str)
        return rounded_str
    except (ValueError, TypeError):
        return '-'

@register.filter
def get_stock_field(result, field: str):
    """
    Returns a field from the content of the result attribute in result
    """
    try:
        if result is None:
            return None

        parent_field, child_field = field.split(':')

        parent = result.get(parent_field, None)
        if parent is None:
            return None
        return parent.get(child_field, None)

    except Exception as e:
        return str(e)

@register.simple_tag
def random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))