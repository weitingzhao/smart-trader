import  core.configures_home as core
import logging
from .utilities.tools import Tools
from .engine import Engine
from .service import Service
from .research import Research
from business.engines.tasks.progress import Progress

# Tier 1. Config. logger and progress
def config(
        name: str = __name__,
        logger: logging.Logger = None,
        need_progress: bool = False) -> core.Config:
    return core.Config(
        name=name,
        logger=logger,
        need_info=not need_progress,
        need_error=not need_progress)

def progress(
        need_progress: bool = False,
        cfg: core.Config = None) -> Progress:
    return Progress(cfg if cfg is not None else config()) if need_progress else None

# Tier 2. Base on Config init Engine and progress
def engine(cfg:core.Config=None, prg:Progress=None) -> Engine:
    return Engine(
        cfg if cfg is not None else config(),
        prg if prg is not None else progress())

def Tools(eng:Engine=None) -> Tools:
    return (eng if eng is not None else engine()).tools


# Tier 3. Base on Engine init Service
def service(eng:Engine=None) -> Service:
    return Service(eng if eng is not None else engine())

# Step 4. Base on Service init Research
def research(svc: Service = None) -> Research:
    return Research(svc if svc is not None else service())



