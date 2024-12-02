from typing import List
from .celery import app
from .controller import *
from celery.contrib.abortable import AbortableTask

def get_tasks() -> List:
    return [
        no_01_fetching,
        no_02_calculating,
        no_03_indexing,
    ]

def get_task_scripts(task_name) -> List:
    if task_name ==  "no_01_fetching":
        return FetchingTask(None, None).job_scripts()
    elif task_name ==  "no_02_calculating":
        return IndexingTask(None, None).job_scripts()
    elif task_name ==  "no_03_indexing":
        return CalculatingTask(None, None).job_scripts()

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


