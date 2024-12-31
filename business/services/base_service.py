from ..engine import Engine
from ..engines.base_engine import BaseEngine


class BaseService(BaseEngine):

    def __init__(self, engine: Engine):
        super().__init__(engine.config)
        self.engine = engine
        self.progress = engine.progress
