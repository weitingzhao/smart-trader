import time
from tqdm import tqdm
from logics.engines.tasks.progress import Progress


class TqdmLogger(tqdm):
    def __init__(self, *args, **kwargs):
        """
        :param args:
        :param kwargs:
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
