import logging
import business.logic as Logic
from business.engine import Engine
from business.service import Service
from business.research import Research
from business.engines.tasks.progress import Progress
from business.utilities.tools import Tools


class Instance:
    def __init__(
            self, name: str = __name__,
            logger: logging.Logger = None, need_progress: bool = False):
        # Tier 1. Config. logger and progress
        self.config = Logic.config(name=name, logger=logger, need_progress=need_progress)
        self.logger = self.config.logger
        self.progress = Progress(self.config) if need_progress else None
        self._engine: Engine = None
        self._service: Service = None
        self._research: Research = None

    def engine(self) -> Engine:
        if self._engine is None:
            self._engine = Logic.engine(self.config, self.progress)
        return self._engine

    def tools(self) -> Tools:
        return self.engine().tools

    def service(self) -> Service:
        if self._service is None:
            self._service = Logic.service(self.engine())
        return self._service

    def research(self) -> Research:
        if self._research is None:
            self._research = Logic.research(self.service())
        return self._research
