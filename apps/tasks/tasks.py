from typing import List
from django_celery_results.models import TaskResult
from logics.logic import Logic, TaskBase
from .celery import app
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


class FetchingTask(TaskBase):

    def __init__(self, celery, data):
        super().__init__(celery, data)

    def job_scripts(self) -> List:
        return [
            {"name":"stock-hist-bars",
             "options": [
                 {
                     "text": "append -> daily interval for 5d period",
                     "value": "append=True,delta=2,period='5d',interval='1d'"
                 },{
                     "text": "append -> min interval for 1d period",
                     "value": "append=True,delta=2,period='1d',interval='1m'"
                 },{
                     "text": "init -> daily interval for max period",
                     "value": "period='5d',interval='1d'"
                 },{
                     "text": "init -> min interval for max period",
                     "value": "period='5d',interval='1m'"
                 }
            ]},
            {"name":"company-info"},
            {"name":"symbols"}
        ]

    def _worker_run(self, script_name: str, logic : Logic, task_result: TaskResult, meta: dict, args: str = None):
        if script_name == 'stock-hist-bars':
            logic.service.fetching().stock_hist_bars_yahoo().run(meta, task_result, args, is_test=False)
        elif script_name == 'company-info':
            logic.service.fetching().company_info_yahoo().run(meta, task_result, args, is_test=False)
        if script_name == 'symbols':
            logic.service.fetching().symbol().fetching_symbol()

class CalculatingTask(TaskBase):

    def __init__(self, celery, data):
        super().__init__(celery, data)

    def job_scripts(self) -> List:
        return [{"name":"volume"}]

    def _worker_run(self, script_name: str, logic : Logic, task_result: TaskResult, meta: dict, args: str = None):
        if script_name == 'volume':
            pass
            # logic.service.saving().symbol().index_symbol()

class IndexingTask(TaskBase):

    def __init__(self, celery, data):
        super().__init__(celery, data)

    def job_scripts(self) -> List:
        return [{"name":"fetching-symbols"}]

    def _worker_run(self, script_name: str, logic : Logic, task_result: TaskResult, meta: dict, args: str = None):
        if script_name == 'indexing-symbols':
            logic.service.saving().symbol().index_symbol()

