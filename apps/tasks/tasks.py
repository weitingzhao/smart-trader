from typing import List
from .celery import app
from .controller import *
from celery.contrib.abortable import AbortableTask
from celery import current_app
from celery import shared_task
from logics.logic import Logic

def get_tasks() -> List:
    return [
        no_01_fetching,
        no_02_calculating,
        no_03_indexing,
        fetching_screening_result,
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

@app.task(bind=True, base=AbortableTask)
def fetching_screening_result(self, data):
    ##### Calculate Open Position ##############
    file_resources = instance.service.fetching().screening().fetching_screening()

    for file_resource in file_resources:
        for file_path, resource in file_resource.items():
            with open(file_path, 'r') as file:
                dataset = resource.import_data(file, format='csv')
                result = resource.import_data(dataset, dry_run=False)
    return result

# Create your views here.
instance = Logic()

# Unregister the task
current_app.tasks.unregister('import_export_celery.tasks.run_export_job')