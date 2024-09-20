import json
import os, time, subprocess
import datetime
from os import listdir
from os.path import isfile, join

from celery.utils.log import get_task_logger
from django.contrib.auth import get_user_model
from django_celery_results.models import TaskResult
from logic.logic import Logic
from logic.engines.notify_engine import Level
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
    "fetching-stock-hist-bars",
    "fetching-company-info",
    "indexing-symbols",
    "fetching-symbols",
]

@app.task(bind=True, base=AbortableTask)
def backend_task(self, data):

    start_time = time.time()  # Record the start time

    def execute_jobs(
            task_name: str,
            logic : Logic,
            task_result:
            TaskResult,
            meta: dict,
            args: str = None):
        """
        :type task_name: str
        :type logic: object
        :type task_result: TaskResult
        :type meta: dict
        """
        if task_name == 'fetching-symbols':
            logic.service.fetching().symbol().fetching_symbol()
        elif task_name == 'indexing-symbols':
            logic.service.saving().symbol().index_symbol()
        elif task_name == 'fetching-company-info':
            logic.service.fetching().company_info_yahoo().run(meta, task_result, args, is_test=False)
        elif task_name == 'fetching-stock-hist-bars':
            logic.service.fetching().stock_hist_bars_yahoo().run(meta, task_result, args, is_test=False)

    def end_log(is_success : bool = False):
        logic.logger.info(
            f"==[END] leftover_count: {len(meta['leftover'])} done_count: {len(meta['done'])} "
            f"cost {(time.time()-start_time):2f} seconds=======>")
        logic.progress.log_flush()
        logic.engine.notify(user).send(
            recipient=user,
            verb=f'{task_name} Task {("done" if is_success else "failed")}!',
            level=Level.INFO if is_success else Level.ERROR,
            description=f'click <a href="#" class="text-xs text-danger" '
                        f'onclick="showFileView(\'{log_file_name}\')">here</a> to view log'
        )

    # Step 1. Get user
    user_id = data.get('user_id')
    if not user_id:
        raise ValueError("User ID is required to send notifications")
    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise ValueError(f"User with ID {user_id} does not exist")

    # Step 1. Get task_name
    task_name = data.get('task_name')
    if not task_name:
        raise ValueError("Task name is required to execute")
    if task_name not in support_tasks:
        raise ValueError(f"Task name '{task_name}' is not supported")

    # Step 1. Get Args
    args = data.get('args', None)

    # Step 2. Prepare logic & Task Result
    logic = Logic("celery task", get_task_logger(__name__), need_progress= True)
    meta = data.get('data', None)

    # Step 3. Base on status of task_result, prepare init load]
    if meta is not None:
        log_file = meta.get("log_file")
        log_file_name = os.path.splitext(os.path.basename(log_file))[0]
    else:
        log_file = get_log_file_path(task_name)
        log_file_name = os.path.splitext(os.path.basename(log_file))[0]
        meta = {
            "input": task_name, "error": "false", "output": "", "status": "STARTED",
            "log_file": log_file,
            "initial": "true", "leftover": [], "done": []
        }
    logic.progress.init_progress(log_file)
    logic.logger.info(
        f"==[START] task_id:{self.request.id} "
        f"leftover_count: {len(meta['leftover'])} done_count: {len(meta['done'])} "
        f"at {datetime.datetime.now()}=======>")

    # Step 4. Update task state
    self.update_state(state='STARTED', meta=meta)
    task_result = TaskResult.objects.get(task_id=self.request.id)
    task_result.result = json.dumps({"exc_type": "Info", "exc_message": meta, "exc_module": "builtins"})
    task_result.save()

    # Step 5. (Main) Run Job
    try:
        execute_jobs(task_name, logic, task_result, meta, args)

        # Done. sent notification
        end_log()
        return meta
    except Exception as e:
        # Error. sent notification
        logic.logger.info(f"run task_id:{self.request.id} Error: {str(e)}")
        end_log()
        raise Exception(meta)
