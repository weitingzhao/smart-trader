from django import template
import random
import string

register = template.Library()

@register.filter(name='replace_value')
def replace_value(value, arg):
    """Removes all values of arg from the given string"""
    return value.replace(arg, ' ').title()

@register.filter
def get_stock_field(result, field: str):
    """
    Returns a field from the content of the result attibute in result
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