import re
import json
from typing import List
from abc import ABC, abstractmethod
from django_celery_results.models import TaskResult
from logics.engines.tasks.tqdm_logger import TqdmLogger


class TaskFetchingWorker(ABC):

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
