import ast
import os
import time
import json
from django.shortcuts import redirect
from celery import current_app
from apps.tasks import tasks as celery_tasks
from django_celery_results.models import TaskResult
from celery.contrib.abortable import AbortableAsyncResult
from apps.tasks.celery import app
from django.http import HttpResponse, Http404
from os import listdir
from os.path import isfile, join
from django.conf import settings
from django.template  import loader


# Create your views here.
def index(request):
    return HttpResponse("INDEX Tasks")

# @login_required(login_url="/login/")
def tasks(request):
    tasks, task_scripts = get_celery_all_tasks()
    context = {
        'cfgError' : None,
        'segment'  : 'tasks',
        'parent'   : 'tools',
        'tasks'    : tasks,
        'task_scripts': task_scripts,
    }
    # django_celery_results_task_result
    task_results = TaskResult.objects.order_by("-id")[:10]
    context["task_results"] = task_results
    html_template = loader.get_template('pages/settings/admin_panel/tasks.html')
    return HttpResponse(html_template.render(context, request))

def run_task(request, task_name):
    """
    Runs a celery task
    :param request:
    :param task_name:
    :return:
    """
    _args   = request.POST.get("args")
    _script_name = request.POST.get("script_name")

    for task in celery_tasks.get_tasks():
        if task["name"] == task_name:
            celery_task = getattr(celery_tasks, task_name)
            data = {
                "args": _args,
                "user_id": request.user.id,
                "script_name": _script_name,
                "task_name": task_name
            }
            celery_task.apply_async(
                args=[data],
                queue=task["queue"],
            )
            # task.delay({
            #     "args": _args,
            #     "user_id": request.user.id,
            #     "script_name": _script_name,
            #     "task_name": task_name
            # })
    time.sleep(1)  # Waiting for task status to update in db
    return redirect("tasks")

def cancel_task(request, task_id):
    """
    Cancels a celery task
    :param request:
    :param task_id:
    :return:
    """
    result = TaskResult.objects.get(task_id=task_id)
    abortable_result = AbortableAsyncResult(result.task_id, task_name=result.task_name, app=app)
    if not abortable_result.is_aborted():
        abortable_result.revoke(terminate=True)

    time.sleep(1)
    return redirect("tasks")


def retry_task(request, task_id):
    # Retrieve the existing task
    task_result = TaskResult.objects.get(task_id=task_id)

    # Reset the task status to PENDING
    task_result.status = 'PENDING'
    task_result.save()

    # Re-queue the task
    task = current_app.tasks[task_result.task_name]
    args_str = task_result.task_args.replace('"', '').replace("'", '"')
    args = ast.literal_eval(args_str)
    kwargs = ast.literal_eval(task_result.result)
    args[0]['data']= kwargs.get('exc_message')[0]
    task.apply_async(args=[args[0]], task_id=task_id)

    # Task 1-second break for db update, to update the task status
    time.sleep(1)
    return redirect("tasks")

def get_celery_all_tasks():
    current_app.loader.import_default_modules()
    tasks_jobs = list(sorted(name for name in current_app.tasks if not name.startswith('celery.')))
    tasks = [{"name": name.split(".")[-1], "script":name, 'scripts': celery_tasks.get_task_scripts(name.split(".")[-1])} for name in tasks_jobs]
    task_scripts = [{"name": name.split(".")[-1], 'scripts': celery_tasks.get_task_scripts(name.split(".")[-1])} for name in tasks_jobs]

    for task in tasks:
        last_task = TaskResult.objects.filter(
            task_name=task["script"]).order_by("date_created").last()
        if last_task:
            task["id"] = last_task.task_id
            task["has_result"] = True
            task["status"] = last_task.status
            task["successful"] = last_task.status == "SUCCESS" or last_task.status == "STARTED"
            task["date_created"] = last_task.date_created
            task["date_done"] = last_task.date_done
            task["result"] = last_task.result
            try:
                task["input"] = json.loads(last_task.result).get("input")
            except:
                task["input"] = ''
    return tasks,task_scripts

def task_output(request):
    '''
    Returns a task output 
    '''
    task_id = request.GET.get('task_id')
    task    = TaskResult.objects.get(id=task_id)
    if not task:
        return ''

    # task.result -> JSON Format
    return HttpResponse( task.result )

def task_log(request):
    '''
    Returns a task LOG file (if located on disk) 
    '''
    task_id  = request.GET.get('task_id')
    task     = TaskResult.objects.get(id=task_id)
    task_log = '{"Result":"NOT FOUND"}'
    if not task: 
        return ''
    try: 
        # Get logs file
        all_logs = [f for f in listdir(settings.CELERY_LOGS_DIR) if isfile(join(settings.CELERY_LOGS_DIR, f))]
        for log in all_logs:
            # Task HASH name is saved in the log name
            if task.task_id in log:
                with open( os.path.join( settings.CELERY_LOGS_DIR, log) ) as f:
                    # task_log -> JSON Format
                    task_log = f.readlines()
                break
    except Exception as e:
        task_log = json.dumps( { 'Error CELERY_LOGS_DIR: ' : str( e) } )
    return HttpResponse(task_log)

def download_log_file(request, file_path):
    path = file_path.replace('%slash%', '/')
    if os.path.exists(path):
        with open(path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(path)
            return response
    raise Http404