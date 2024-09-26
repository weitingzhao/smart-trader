import logics
import logging
from logics.engines.tasks.progress import Progress
from logics.utilities.tools import Tools
import  core.configures_home as core

class Logic:

    def __init__(self,
                 name: str = __name__,
                 logger: logging.Logger = None,
                 need_progress: bool = False):

        # Tier 1. Config. logger and progress
        self.config = core.Config( name=name, logger=logger, need_info=not need_progress, need_error=not need_progress)
        self.logger = self.config.logger
        self.progress = Progress(self.config) if need_progress else None

        # Tier 2. Base on Config init Engine and progress
        self.engine = logics.Engine(self.config, self.progress)
        self.tools: Tools = self.engine.tools

        # Tier 3. Base on Engine init Service
        self.service = logics.Service(self.engine)

        # Step 4. Base on Service init Analyze
        self.research = logics.Research(self.service)

