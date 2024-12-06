from typing import List
from logics.logic import Logic
from .base_task import BaseTask
from django_celery_results.models import TaskResult

class IndexingTask(BaseTask):

    def __init__(self, celery, data):
        super().__init__(celery, data)

    def job_scripts(self) -> List:
        return [{"name":"indexing-symbols"}]

    def _worker_run(self, script_name: str, logic : Logic, task_result: TaskResult, meta: dict, args: str = None):
        if script_name == 'indexing-symbols':
            logic.service.saving().symbol().index_symbol()
