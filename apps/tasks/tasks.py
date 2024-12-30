from typing import List
from .celery import app
from .controller import *
from celery.contrib.abortable import AbortableTask
from celery import current_app

def get_tasks() -> List:
    return [
        no_01_fetching,
        no_02_calculating,
        no_03_indexing,
        no_04_screening,
        no_05_snapshot,
    ]

def get_task_scripts(task_name) -> List:
    if task_name ==  "no_01_fetching":
        return FetchingTask(None, None).job_scripts()
    elif task_name ==  "no_02_calculating":
        return CalculatingTask(None, None).job_scripts()
    elif task_name ==  "no_03_indexing":
        return IndexingTask(None, None).job_scripts()
    elif task_name ==  "no_04_screening":
        return ScreeningTask(None, None).job_scripts()
    elif task_name == "no_05_snapshot":
        return SnapshotTask(None, None).job_scripts()

@app.task(bind=True, base=AbortableTask)
def no_01_fetching(self, data):
    task = FetchingTask(self, data)
    task.run()

@app.task(bind=True, base=AbortableTask)
def no_02_calculating(self, data):
    task = CalculatingTask(self, data)
    task.run()

@app.task(bind=True, base=AbortableTask)
def no_03_indexing(self, data):
    task = IndexingTask(self, data)
    task.run()

@app.task(bind=True, base=AbortableTask)
def no_04_screening(self, data):
    task = ScreeningTask(self, data)
    task.run()

@app.task(bind=True, base=AbortableTask)
def no_05_snapshot(self, data):
    task = SnapshotTask(self, data)
    task.run()

# Unregister the task
current_app.tasks.unregister('import_export_celery.tasks.run_export_job')