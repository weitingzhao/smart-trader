import json
from core.configures_home import Config
from pathlib import Path
from datetime import datetime
from logic.engines.base_engine import BaseEngine


class JsonEngine(BaseEngine):

    def __init__(self, config: Config, path: Path):
        super().__init__(config)
        self.Path = path

    def is_file(self):
        return self.Path.is_file()

    def load(self):
        return json.loads(self.Path.read_bytes())

    def save(self, data: object):
        self.Path.write_text(json.dumps(data, indent=3, cls=JsonEngine.Encoder))

    class Encoder(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, datetime):
                return o.isoformat()
            return super().default(o)
