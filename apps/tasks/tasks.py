import os, time, subprocess
import datetime
from os import listdir
from os.path import isfile, join
from django.contrib.auth import get_user_model
from logic.engines.notify_engine import Level
from logic.logic import Logic
from .celery import app
from celery.contrib.abortable import AbortableTask
from django.conf import settings


def get_scripts():
    """
    Returns all scripts from 'ROOT_DIR/celery_scripts'
    """
    raw_scripts = []
    scripts     = []
    ignored_ext = ['db', 'txt']

    try:
        raw_scripts = [f for f in listdir(settings.CELERY_SCRIPTS_DIR) if isfile(join(settings.CELERY_SCRIPTS_DIR, f))]
    except Exception as e:
        return None, 'Error CELERY_SCRIPTS_DIR: ' + str( e ) 

    for filename in raw_scripts:

        ext = filename.split(".")[-1]
        if ext not in ignored_ext:
           scripts.append( filename )

    return scripts, None           

def write_to_log_file(logs, script_name):
    log_file_path = get_log_file_path(script_name)
    with open(log_file_path, 'w') as log_file:
        log_file.write(logs)
    return log_file_path

def get_log_file_path(script_name) -> str:
    """
    Writes logs to a log file with formatted name in the CELERY_LOGS_DIR directory.
    """
    script_base_name = os.path.splitext(script_name)[0]  # Remove the .py extension
    current_time = datetime.datetime.now().strftime("%y%m%d-%H%M%S")
    log_file_name = f"{script_base_name}-{current_time}.log"
    return os.path.join(settings.CELERY_LOGS_DIR, log_file_name)


@app.task(bind=True, base=AbortableTask)
def execute_script(self, data: dict):
    """
    This task executes scripts found in settings.CELERY_SCRIPTS_DIR and logs are later generated and stored in settings.CELERY_LOGS_DIR
    :param data dict: contains data needed for task execution. Example `input` which is the script to be executed.
    :rtype: None
    """
    script = data.get("script")
    args   = data.get("args")

    print( '> EXEC [' + script + '] -> ('+args+')' )

    scripts, err_info = get_scripts()

    if script and script in scripts:
        # Executing related script
        script_path = os.path.join(settings.CELERY_SCRIPTS_DIR, script)
        process = subprocess.Popen(
            f"python {script_path} {args}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(8)

        exit_code = process.wait()
        error = False
        status = "STARTED"
        if exit_code == 0:  # If script execution successful
            logs = process.stdout.read().decode()
            status = "SUCCESS"
        else:
            logs = process.stderr.read().decode()
            error = True
            status = "FAILURE"

        log_file = write_to_log_file(logs, script)

        return {"logs": logs, "input": script, "error": error, "output": "", "status": status, "log_file": log_file}



support_tasks = [
    "indexing-symbols",
    "fetching-symbols",
    "fetching-company-info"
]

@app.task(bind=True, base=AbortableTask)
def backend_task(self, data):
    # user_id
    user_id = data.get('user_id')
    if not user_id:
        raise ValueError("User ID is required to send notifications")

    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise ValueError(f"User with ID {user_id} does not exist")

    # task_name
    task_name = data.get('task_name')
    if not task_name:
        raise ValueError("Task name is required to execute")
    if task_name not in support_tasks:
        raise ValueError(f"Task name '{task_name}' is not supported")

    # Setup logger
    instance = Logic("celery task")
    log_file_path = get_log_file_path(task_name)
    instance.progress.init_progress(log_file_path)

    self.update_state(
        state='PROGRESS',
        meta={"input": task_name, "error": False, "output": "", "status": "SUCCESS", "log_file": log_file_path}
    )
    # Execute the task
    if task_name == 'fetching-symbols':
        instance.service.fetching().symbol().fetching_symbol()
    elif task_name == 'indexing-symbols':
        instance.service.saving().symbol().index_symbol()
    elif task_name == 'fetching-company-info':
        instance.service.fetching().symbol().fetching_symbols_info()

    # Process done. Sent notification
    log_file_name = os.path.splitext(os.path.basename(log_file_path))[0]
    instance.engine.notify(user).send(
        recipient=user,
        verb=f'{task_name} Task done!',
        level=Level.INFO,
        description=f'click <a href="#" class="text-xs text-danger" onclick="showFileView(\'{log_file_name}\')">here</a> to view log'
    )

    return {"input": task_name, "error": False, "output": "", "status": "SUCCESS", "log_file": log_file_path}