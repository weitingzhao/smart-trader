from django import template
import random
import string

register = template.Library()

@register.filter(name='replace_value')
def replace_value(value, arg):
    """Removes all values of arg from the given string"""
    return value.replace(arg, ' ').title()

@register.simple_tag
def random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))