from django.contrib.auth.models import AnonymousUser
from pathlib import Path
from .utilities.plugin import Plugin
from . import engines as engine
from core.configures_home import Config
from .engines.tasks.progress import  Progress
from .engines.base_engine import BaseEngine


class Engine(BaseEngine):
    def __init__(self, config: Config, progress: Progress):
        super().__init__(config)
        self.progress: Progress = progress

    def web(self, url: str) -> engine.WebEngine:
        return engine.WebEngine(self.config, url)

    def db(self) -> engine.PgSqlEngine:
        return engine.PgSqlEngine(self.config)

    def sql_alchemy(self) -> engine.SqlAlchemyEngine:
        return engine.SqlAlchemyEngine(self.config)

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

    def notify(self, sender: AnonymousUser) -> engine.NotifyEngine:
        return engine.NotifyEngine(self.config, sender)

    def plugin(self) -> Plugin:
        return Plugin()