import importlib.util
import logging
import string
import sys
from pathlib import Path
import random
from typing import Union, Type
from types import ModuleType
import requests
from tqdm import tqdm

class Tools:

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    @staticmethod
    def random_char(length):
        return "".join(random.choice(string.ascii_lowercase) for _ in range(length))

    def web_response(self, url: str):
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            self.logger.error(f"Error fetching data: {response.status_code}")
            return None

    def load_module(self, module_str: str) -> Union[ModuleType, Type]:
        """
        Load a module specified by the given string.

        Arguments
        module_str (str): Module filepath, optionally adding the class name
            with format <filePath>:<className>

        Raises:
        ModuleNotFoundError: If module is not found
        AttributeError: If class name is not found in module.

        Returns: ModuleType
        """
        class_name = None
        module_path = module_str

        if "|" in module_str:
            module_path, class_name = module_str.split("|")

        module_path = Path(module_path).expanduser().resolve()
        spec = importlib.util.spec_from_file_location(module_path.stem, module_path)

        if not spec or not spec.loader:
            raise ModuleNotFoundError(f"Module not found: {module_path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_path.stem] = module

        spec.loader.exec_module(module)
        return getattr(module, class_name) if class_name else module


class TqdmLogger(tqdm):
    def __init__(self, *args, **kwargs):
        self.logger = kwargs.pop("logger", None)
        self.elapsed = 0 # initialize elapsed attribute
        super().__init__(*args, **kwargs)

    def display(self, msg=None, pos=None):
        if msg is None:
            msg = self.format_meter(self.n, self.total, self.elapsed)
        if self.logger:
            self.logger.info(msg)
        else:
            super().display(msg, pos)