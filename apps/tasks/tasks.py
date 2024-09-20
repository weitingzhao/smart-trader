from typing import List
from django_celery_results.models import TaskResult
from logic.logic import Logic, TaskBase
from .celery import app
from celery.contrib.abortable import AbortableTask


def get_scripts():
    """
    Returns all scripts from 'ROOT_DIR/celery_scripts'
    """
    support_tasks = []

    task = FetchingDailyTask(None, None)
    support_tasks.extend(task.support_tasks())

    return support_tasks


@app.task(bind=True, base=AbortableTask)
def fetching_daily_task(self, data):
    task = FetchingDailyTask(self, data)
    task.run()

class FetchingDailyTask(TaskBase):

    def __init__(self, celery, data):
        super().__init__(celery, data)

    def support_tasks(self) -> List:
        return ["fetching-stock-hist-bars"]

    def _worker_run(self,
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


# support_tasks = [
#     "fetching-stock-hist-bars",
#     "fetching-company-info",
#     "indexing-symbols",
#     "fetching-symbols",
# ]
