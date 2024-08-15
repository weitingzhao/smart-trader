from core.configures_home import Config
from pathlib import Path
import logic.engines as engine
from logic.utilities.plugin import Plugin
from logic.engines.base_engine import BaseEngine


class Engine(BaseEngine):
    def __init__(self, config: Config):
        super().__init__(config)

    def web(self, url: str) -> engine.WebEngine:
        return engine.WebEngine(self.config, url)

    def db(self) -> engine.PgSqlEngine:
        return engine.PgSqlEngine(self.config)

    def json_data(self, *args):
        return self.json(root=self.config.ROOT_Data, *args)

    def json_research(self, *args):
        return self.json(root=self.config.ROOT_Research, *args)

    def json_user(self):
        return self.json(root=self.config.FILE_user)

    def json(self, root: Path, *args):
        path = self.path_exist(root.joinpath(*args))
        return engine.JsonEngine(self.config, path)

    def csv(self, *args) -> engine.CsvEngine:
        path = self.config.ROOT_Data.joinpath(*args)
        self.path_exist(path)
        return engine.CsvEngine(self.config, path)

    def plugin(self) -> Plugin:
        return Plugin()