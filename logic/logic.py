import re
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
        self.log_stream = StringIO()
        task_log_handler = logging.StreamHandler(self.log_stream)
        task_log_handler.setLevel(logging.INFO)
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

        # if round(current_percent) <= self.last_displayed_percent:
        #     return

        self.last_displayed_percent = round(current_percent)
        if msg is None:
            msg = self.format_meter(self.n, self.total, self.elapsed)
        if self.progress:
            self.progress.logger.info(msg)
            self.progress.flush()
        else:
            super().display(msg, pos)

class TaskBuilder(ABC):

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

                self.logger.info(f"Success : {record}")
            except Exception as e:
                self.logger.error(f"Error :  {record}  error: {e}")
                error_list.append({"Index:": record, "error": str(e)})

            # Simulate real workload
            # if i % 20 == 0:
            #     raise ValueError("Test error")

        # Flush the task result at last time
        flush_to_task_result()

        return error_list, meta
