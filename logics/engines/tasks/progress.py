import logging
from io import StringIO
import core.configures_home as core

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
