from typing import List
from .instance import Instance
from .base_task import BaseTask
from django_celery_results.models import TaskResult

class ScreeningTask(BaseTask):

    def __init__(self, celery, data):
        super().__init__(celery, data)

    def job_scripts(self) -> List:
        return [{"name":"None"}]

    def _worker_run(self, script_name: str, instance : Instance, task_result: TaskResult, meta: dict, args: str = None):
        # Step 1.  Get the screening operations
        instance.service().fetching().screening().screening_operation()


