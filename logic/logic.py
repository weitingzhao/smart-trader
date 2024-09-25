import re, os, datetime
import json
from abc import ABC, abstractmethod
import time
from typing import List
from tqdm import tqdm
from django_celery_results.models import TaskResult
import logic
import logging
from io import StringIO
from logic.utilities.tools import Tools
import  core.configures_home as core
from logic.engines.notify_engine import Level
from celery.utils.log import get_task_logger
from django.contrib.auth import get_user_model
from django.conf import settings

class Logic:

    def __init__(self,
                 name: str = __name__,
                 logger: logging.Logger = None,
                 need_progress: bool = False):

        # Tier 1. Config.
        self.config = core.Config(
            name=name, logger=logger,
            need_info=not need_progress,
            need_error=not need_progress)
        self.progress = Progress(self.config) if need_progress else None
        self.logger = self.config.logger

        # Tier 2. Base on Config init Engine and progress
        self.engine = logic.Engine(self.config, self.progress)
        self.tools: Tools = self.engine.tools

        # Tier 3. Base on Engine init Service
        self.service = logic.Service(self.engine)

        # Step 4. Base on Service init Analyze
        self.research = logic.Research(self.service)


class Progress:
    def __init__(self, config: core.Config):
        self.config = config
        self.logger: logging.Logger = self.config.logger

        self.log_file_path = None
        self.log_stream = None
        self.log_flush = None

    def init_progress(self, log_file_path: str):
        # step 1. User & log path
        self.log_file_path = log_file_path

        # step 2  prepare new handler for logger
        if not any(handler.name == "Logic: Progress [Info]" for handler in self.logger.handlers):
            self.log_stream = StringIO()
            task_log_handler = logging.StreamHandler(self.log_stream)
            task_log_handler.setLevel(logging.INFO)
            task_log_handler.name = "Logic: Progress [Info]"
            self.logger.addHandler(task_log_handler)

        # assign function for log and notification
        def flush():
            logs = self.log_stream.getvalue()
            with open(self.log_file_path, 'a') as log_file:
                log_file.write(logs)
            self.log_stream.truncate(0) # Clear the log stream after flushing
            self.log_stream.seek(0)

        self.log_flush = flush
        return True

    def flush(self):
        if self.log_flush:
            self.log_flush()
        return True


class TqdmLogger(tqdm):
    def __init__(self, *args, **kwargs):
        """
        :type kwargs: Progress
        """
        self.progress : Progress = kwargs.pop("progress", None)
        self.start_time = time.time()  # initialize start_time attribute
        self.last_displayed_percent = 0  # initialize last displayed percent
        super().__init__(*args, **kwargs)

    def display(self, msg=None, pos=None):
        self.elapsed = time.time() - self.start_time  # update elapsed attribute
        current_percent = (self.n / self.total) * 100 if self.total else 0  # calculate current percent

        if round(current_percent) <= self.last_displayed_percent:
            return

        self.last_displayed_percent = round(current_percent)
        if msg is None:
            msg = self.format_meter(self.n, self.total, self.elapsed)
        if self.progress:
            self.progress.logger.info(msg)
            self.progress.flush()
        else:
            super().display(msg, pos)

class TaskWorker(ABC):

    def __init__(self):
        super().__init__()

    # Step 1.
    # Simulate for test use only
    @abstractmethod
    def _get_init_load_test(self) -> List:
        """Abstract method that must be implemented in any subclass"""
        pass
    @abstractmethod
    def _get_init_load(self)->List:
        """Abstract method that must be implemented in any subclass"""
        pass

    # Step 2.
    def _before_fetching(self, records: List) -> any:
        return None

    # Step 3.
    @abstractmethod
    def _fetching_detail(self, record: str, tools: any):
        """Abstract method that must be implemented in any subclass"""
        pass

    # Builder pattern
    def run(self, meta: dict, task_result:TaskResult, args: str = None, is_test : bool = False):

        if not isinstance(meta, dict):
            raise ValueError("task_kwargs must be a dictionary or a JSON string")

        if args:
            pattern = re.compile(r"(\w+)=['\"]?([^,'\"]+)['\"]?")
            matches = pattern.findall(args)
            self.args = {key: value for key, value in matches}
        else:
            self.args = {}

        def flush_to_task_result():
            meta["initial"] = "false"
            if task_result:
                task_result.result = json.dumps({"exc_type": "Info", "exc_message": meta, "exc_module": "builtins"})
                task_result.save()

        # Check if initial load is required. if not. means it's failed and try again
        if meta.get("initial", "false") ==  "true":
            meta["leftover"].extend(self._get_init_load_test() if is_test else self._get_init_load())
            meta["initial"] = "false"

        # Before fetching
        tools = self._before_fetching(meta["leftover"])

        # Fetch the data
        leftover_copy = meta["leftover"][:] # Create a copy of meta["leftover"]
        error_list = []
        i = 0
        for record in TqdmLogger(leftover_copy, progress=self.progress):
            try:
                self._fetching_detail(record, tools)

                # Move record from leftover to done
                meta["done"].append(record)
                meta["leftover"].remove(record)

                i = i +1
                if i % 50 == 0:
                    flush_to_task_result()

                # self.logger.info(f"Success : {record}")
            except Exception as e:
                self.logger.error(f"Error :  {record}  error: {e}")
                error_list.append({"Index:": record, "error": str(e)})

            # Simulate real workload
            # if i % 20 == 0:
            #     raise ValueError("Test error")

        # Flush the task result at last time
        flush_to_task_result()

        return error_list, meta


class TaskBase(ABC):

    def __init__(self, celery, data):
        self.start_time = time.time()  # Record the start time

        self.celery = celery
        self.data = data
        super().__init__()

    @abstractmethod
    def _worker_run(self,
             task_name: str,
             logic : Logic,
             task_result:
             TaskResult,
             meta: dict,
             args: str = None):
        """Abstract method that must be implemented in any subclass"""
        pass

    # Simulate for test use only
    @abstractmethod
    def support_tasks(self) -> List:
        """Abstract method that must be implemented in any subclass"""
        pass


    def write_to_log_file(self, logs, script_name):
        log_file_path = self.get_log_file_path(script_name)
        with open(log_file_path, 'w') as log_file:
            log_file.write(logs)
        return log_file_path

    def get_log_file_path(self, script_name) -> str:
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
        User = get_user_model()
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValueError(f"User with ID {user_id} does not exist")

        # Step 1.b. Get task_name
        task_name = self.data.get('task_name')
        if not task_name:
            raise ValueError("Task name is required to execute")
        if task_name not in self.support_tasks():
            raise ValueError(f"Task name '{task_name}' is not supported")

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
            log_file = self.get_log_file_path(task_name)
            log_file_name = os.path.splitext(os.path.basename(log_file))[0]
            meta = {
                "input": task_name, "error": "false", "output": "", "status": "STARTED",
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
        def end_log(log_file_name, is_success: bool = False):
            logic.logger.info(
                f"==[END] leftover_count: {len(meta['leftover'])} done_count: {len(meta['done'])} "
                f"cost {(time.time() - self.start_time):2f} seconds=======>")
            logic.progress.log_flush()
            logic.engine.notify(user).send(
                recipient=user,
                verb=f'{task_name} Task {("done" if is_success else "failed")}!',
                level=Level.INFO if is_success else Level.ERROR,
                description=f'click <a href="#" class="text-xs text-danger" '
                            f'onclick="showFileView(\'{log_file_name}\')">here</a> to view log'
            )
        try:
            self._worker_run(task_name, logic, task_result, meta, args)
            # Done. sent notification
            end_log(log_file_name, is_success=True)
            return meta
        except Exception as e:
            # Error. sent notification
            logic.logger.info(f"run task_id:{self.celery.request.id} Error: {str(e)}")
            end_log(log_file_name, is_success=False)
            raise Exception(meta)
