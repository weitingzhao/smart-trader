import io
import pandas as pd
from core.configures_home import Config
from pathlib import Path
from pandas import DataFrame
from logics.engines.base_engine import BaseEngine


class CsvEngine(BaseEngine):
    def __init__(self, config: Config, path: Path):
        super().__init__(config)
        self.Path = path
        if not self.Path.exists():
            # Create any necessary parent directories
            self.Path.parent.mkdir(parents=True, exist_ok=True)
            # Create the file
            self.Path.touch()

    def save_str(self, data: str):
        df = pd.read_csv(io.StringIO(data), header=None)  # Create DataFrame
        df.to_csv(self.Path, index=True, header=True)  # Save to CSV

    def save_df(self, df: DataFrame):
        df.to_csv(self.Path, index=True, header=True)  # Save to CSV

