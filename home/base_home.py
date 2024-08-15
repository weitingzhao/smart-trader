import  core.configures_home as core
from logic.utilities.tools import Tools
import logic
import logging


class BaseHome:
    def __init__(self):
        # Tier 1. Config.
        self.config = core.Config()
        self.logger: logging.Logger = self.config.logger
        self.tools: Tools = Tools(self.config.logger)

        # Tier 2. Base on Config init Engine
        self.engine = logic.Engine(self.config)

        # Tier 3. Base on Engine init Service
        self.service = logic.Service(self.engine)

        # Step 4. Base on Service init Analyze
        self.research = logic.Research(self.service)
