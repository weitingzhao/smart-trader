import json
from abc import ABC, abstractmethod
from typing import List

from django_celery_results.models import TaskResult
from tqdm import tqdm
import logic
import logging
from io import StringIO
from logic.utilities.tools import Tools
import  core.configures_home as core


class Logic:

    def __init__(self, name: str = __name__):

        # Tier 1. Config.
        self.config = core.Config(name)
        self.logger: logging.Logger = self.config.logger
        self.progress = Progress(self.config)

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

        # step 2. Redefine config logger
        # Disable info and error handler when progress is enable
        self.config.initial_log(self.config.__name__, need_info=False, need_error=False)
        # prepare new handler for logger
        self.log_stream = StringIO()
        task_log_handler = logging.StreamHandler(self.log_stream)
        task_log_handler.setLevel(logging.INFO)
        self.logger.addHandler(task_log_handler)

        # assign function for log and notification
        def flush():
            logs = self.log_stream.getvalue()
            with open(self.log_file_path, 'w') as log_file:
                log_file.write(logs)

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
        self.elapsed = 0 # initialize elapsed attribute
        super().__init__(*args, **kwargs)

    def display(self, msg=None, pos=None):
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

    @abstractmethod
    def _get_init_load(self)->List:
        """Abstract method that must be implemented in any subclass"""
        pass

    def _before_fetching(self, records: List) -> any:
        return None

    @abstractmethod
    def _fetching_detail(self, record: str, tools: any):
        """Abstract method that must be implemented in any subclass"""
        pass

    def run(self, task_result:TaskResult, meta: dict):

        if not isinstance(meta, dict):
            raise ValueError("task_kwargs must be a dictionary or a JSON string")

        def flush_to_task_result():
            meta["initial"] = "false"
            task_result.result = json.dumps({"exc_type": "Info", "exc_message": meta, "exc_module": "builtins"})
            task_result.save()

        # Check if initial load is required
        if meta.get("initial", "false") ==  "true":
            meta["leftover"].extend(self._get_init_load())
            meta["initial"] = "false"

        # Before fetching
        tools = self._before_fetching(meta["leftover"])

        # Fetch the data
        error_list = []
        i = 0
        for record in TqdmLogger(meta["leftover"], progress=self.progress):
            try:
                self._fetching_detail(record, tools)

                # Move record from leftover to done
                meta["done"].append(record)
                meta["leftover"].remove(record)

                i = i +1
                if i % 5 == 0:
                    flush_to_task_result()

                self.logger.info(f"Success: fetch {record} info")
            except Exception as e:
                self.logger.error(f"Error: fetch {record} info - got Error:{e}")
                error_list.append({"symbol": record, "error": str(e)})

            if i % 8 == 0:
                raise ValueError("Test error")

        # Flush the task result at last time
        flush_to_task_result()

        return error_list, meta
