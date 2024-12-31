from typing import List
from .instance import Instance
from .base_task import BaseTask
from django_celery_results.models import TaskResult


class FetchingTask(BaseTask):

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
            {"name":"symbols"},
        ]

    def _worker_run(self, script_name: str, instance : Instance, task_result: TaskResult, meta: dict, args: str = None):

        if script_name == 'stock-hist-bars':
            instance.service().fetching().stock_hist_bars_yahoo().run(meta, task_result, args, is_test=False)
        elif script_name == 'company-info':
            instance.service().fetching().company_info_yahoo().run(meta, task_result, args, is_test=False)
        if script_name == 'symbols':
            instance.service().fetching().symbol().fetching_symbol()
