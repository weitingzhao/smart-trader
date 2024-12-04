import os
from logics.engine import Engine
from logics.services.base_service import BaseService
import pandas as pd
import yfinance as yf
from apps.common.models import *
from alpha_vantage.fundamentaldata import FundamentalData



class ScreeningService(BaseService):

    def __init__(self, engine: Engine):
        super().__init__(engine)
        self.API_KEY = self.config.API_KEY_Alphavantage

    def fetching_screening(self) -> list:
        file_paths = []
        folder_screenings = self.config.FOLDER_Screenings

        for root, dirs, files in os.walk(folder_screenings):
            for dir_date in dirs:
                dir_daily_screening = os.path.join(root, dir_date)
                for sub_root, sub_dirs, sub_files in os.walk(dir_daily_screening):
                    for file in sub_files:
                        file_path = os.path.join(sub_root, file)
                        file_paths.append(file_path)

        return file_paths