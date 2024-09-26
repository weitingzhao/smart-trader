import json
import time
import os, datetime
from typing import List
from logics.logic import Logic
from django.conf import settings
from abc import ABC, abstractmethod
from celery.utils.log import get_task_logger
from logics.engines.notify_engine import Level
from django.contrib.auth import get_user_model
from django_celery_results.models import TaskResult

class BaseTask(ABC):

    def __init__(self, celery, data):
        self.start_time = time.time()  # Record the start time

        self.celery = celery
        self.data = data
        super().__init__()

    @abstractmethod
    def _worker_run(
            self, script_name: str, logic : Logic,
            task_result: TaskResult, meta: dict, args: str = None):
        """
        Abstract method that must be implemented in any subclass
        :param script_name: str
        :param logic: Logic
        :param task_result: TaskResult
        :param meta: dict
        :param args: str
        :return: None
        """
        pass

    # Simulate for test use only
    @abstractmethod
    def job_scripts(self) -> List:
        """Abstract method that must be implemented in any subclass"""
        pass

    def write_to_log_file(self, logs, script_name):
        log_file_path = self.get_log_file_path(script_name)
        with open(log_file_path, 'w') as log_file:
            log_file.write(logs)
        return log_file_path

    @staticmethod
    def get_log_file_path(script_name) -> str:
        """
        Writes logs to a log file with formatted name in the CELERY_LOGS_DIR directory.
        """
        script_base_name = os.path.splitext(script_name)[0]  # Remove the .py extension
        current_time = datetime.datetime.now().strftime("%y%m%d-%H%M%S")
        log_file_name = f"{script_base_name}-{current_time}.log"
        return os.path.join(settings.CELERY_LOGS_DIR, log_file_name)


    def run(self):

        # Step 1.a. Get user
        user_id = self.data.get('user_id')
        if not user_id:
            raise ValueError("User ID is required to send notifications")
        user_model = get_user_model()
        try:
            user = user_model.objects.get(id=user_id)
        except user_model.DoesNotExist:
            raise ValueError(f"User with ID {user_id} does not exist")

        # Step 1.b. Get task_name
        script_name = self.data.get('script_name')
        if not script_name:
            raise ValueError("Script Name is required to execute")
        # Extract script names from job_scripts
        script_names = [script['name'] for script in self.job_scripts()]
        if script_name not in script_names:
            raise ValueError(f"Script '{script_name}' is not supported")

        # Step 1.c.  Get args & meta
        args = self.data.get('args', None)
        meta = self.data.get('data', None)

        # Step 2.a. Setup logic
        logic = Logic("celery task", get_task_logger(__name__), need_progress= True)

        # Step 2.b. Base on status of task_result, prepare init load
        if meta is not None:
            log_file = meta.get("log_file")
            log_file_name = os.path.splitext(os.path.basename(log_file))[0]
        else:
            log_file = self.get_log_file_path(script_name)
            log_file_name = os.path.splitext(os.path.basename(log_file))[0]
            meta = {
                "input": script_name, "error": "false", "output": "", "status": "STARTED",
                "log_file": log_file,
                "initial": "true", "leftover": [], "done": []
            }

        # Step 2.c Setup logic's progress & logger
        logic.progress.init_progress(log_file)
        logic.logger.info(
            f"==[START] task_id:{self.celery.request.id} "
            f"leftover_count: {len(meta['leftover'])} done_count: {len(meta['done'])} "
            f"at {datetime.datetime.now()}=======>")

        # Step 3. Update celery task state
        self.celery.update_state(state='STARTED', meta=meta)
        task_result = TaskResult.objects.get(task_id=self.celery.request.id)
        task_result.result = json.dumps({"exc_type": "Info", "exc_message": meta, "exc_module": "builtins"})
        task_result.save()

        # Step 4. (Main) Run Job
        def end_log(is_success: bool = False):
            logic.logger.info(
                f"==[END] leftover_count: {len(meta['leftover'])} done_count: {len(meta['done'])} "
                f"cost {(time.time() - self.start_time):2f} seconds=======>")
            logic.progress.log_flush()
            logic.engine.notify(user).send(
                recipient=user,
                verb=f'{script_name} Job {("done" if is_success else "failed")}!',
                level=Level.INFO if is_success else Level.ERROR,
                description=f'click <a href="#" class="text-xs text-danger" '
                            f'onclick="showFileView(\'{log_file_name}\')">here</a> to view log'
            )
        try:
            self._worker_run(script_name, logic, task_result, meta, args)
            # Done. sent notification
            end_log(is_success=True)
            return meta
        except Exception as e:
            # Error. sent notification
            logic.logger.info(f"run task_id:{self.celery.request.id} Error: {str(e)}")
            end_log(is_success=False)
            raise Exception(meta)
