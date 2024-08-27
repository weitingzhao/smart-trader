# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import json
import os
import ast
from django import template
from django.conf import settings
from django.template.defaultfilters import length

register = template.Library()

@register.filter
def date_format(date):
    """
    Returns a formatted date string
    Format:  `Year-Month-Day-Hour-Minute-Second`
    Example: `2022-10-10-00-20-33`
    :param date datetime: Date object to be formatted
    :rtype: str
    """
    try:
        return date.strftime(r'%Y-%m-%d-%H-%M-%S')
    except:
        return date

@register.filter
def get_result_field(result, field: str):
    """
    Returns a field from the content of the result attibute in result 
    Example: `result.result['field']`
    :param result AbortableAsyncResult: Result object to get field from
    :param field str: Field to return from result object
    :rtype: str
    """
    try:
        if result is None:
            return None
        if result.status == "SUCCESS":
            result = json.loads(result.result)
            if result:
                return result.get(field)
        if result.status == 'FAILURE' or result.status == 'FAILURE':
            result = json.loads(result.result)
            if result:
                exc_message = result.get('exc_message', None)
                if exc_message is None or length(exc_message) <= 0:
                    return None
                return exc_message[0].get(field)
        elif result.status == 'STARTED':
            result = result.result.replace("'", '"')
            result = json.loads(result)
            exc_message = result.get('exc_message', None)
            if exc_message is None:
                return None
            return exc_message.get(field)
        return None
    except Exception as e:
        return str(e)


@register.filter
def get_result_log_file(result):
    log_file = get_result_field(result, 'log_file')
    if log_file is None:
        return None
    log_file_name = os.path.splitext(os.path.basename(log_file))[0]
    return log_file_name


@register.filter
def get_task_args_field(result, field: str):
    task_args = result.task_args.strip('"')
    task_args = task_args.replace("\\\\'",'')
    task_args_tuple = ast.literal_eval(task_args)
    task_args_dict = task_args_tuple[0]
    if task_args_dict:
        return task_args_dict.get(field)


@register.filter
def log_file_path(path):
    file_path = path.split("tasks_logs")[1]
    return file_path


@register.filter
def log_to_text(path):
    path = path.lstrip('/')
    full_path = os.path.join(settings.CELERY_LOGS_DIR, path)
    try:
        with open(full_path, 'r') as file:
            text = file.read()
        return text
    except:
        return 'NO LOGS'
