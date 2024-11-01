import json

from django import template
import random
import string
from apps.common.models import *

register = template.Library()

@register.filter
def action_lookup(value, arg):
    # Lookup dictionaries
    return dict(ActionChoices.choices).get(arg)

@register.filter
def timing_lookup(value, arg):
    # Lookup dictionaries
    return dict(TimingChoices.choices).get(arg)

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