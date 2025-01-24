import decimal
import psycopg2
import pandas as pd
import numpy as np
from core.configures_home import Config
from .base_engine import BaseEngine
from sqlalchemy import create_engine
from django.conf import settings
from django.core.paginator import Paginator

class SqlAlchemyEngine(BaseEngine):

    def __init__(self, config: Config):
        super().__init__(config)
        self.engine = settings.DB_ENGINE
        self.name = settings.DB_NAME
        self.username = settings.DB_USERNAME
        self.password = settings.DB_PASS.replace('@', '%40')
        self.host =  settings.DB_HOST
        self.port = settings.DB_PORT

        self.conStr = f'postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.name}'


    def create_engine(self):
        return create_engine(self.conStr)


    def query_pagination(
            self,
            # SQL
            count_sql: str, main_sql: str,
            # Where
            search_column: str, search_value: str,
            # Sort
            sort_default_column: str, sort_column: str, sort_direction: str = 'ASC',
            # Pagination
            page_size: int = 10, page_number: int = 1):

        # Where parameters
        where_sql = " where 1=1 "
        if len(search_value) > 0:
            params = (f'%{search_value}%',)
            where_sql += f" and ({search_column}) ILIKE %s"
        else:
            params = ()

        # Order parameters
        sort_sql = sort_default_column
        if sort_column and sort_direction:
            # 将它们连接起来，通常可以用逗号或其他分隔符
            sort_sql = f" {sort_column} {sort_direction}"

        # Step 1. Pagination offset
        offset = (page_number - 1) * page_size

        # Step 2. Total count Query
        count_query = f"""
            {count_sql}
            SELECT COUNT(*) FROM count sd {where_sql};
        """
        # Step 3 Main data Query
        main_query = f"""
            {main_sql}
            {where_sql}
            ORDER BY {sort_sql}
            LIMIT {page_size} OFFSET {offset};
        """

        try:
            # Create the engine
            engine = self.create_engine()

            # Query the data
            snapshot_df = pd.read_sql_query(main_query, engine, params=params)
            snapshot_df = snapshot_df.replace({np.nan: None})  # Replace NaN with None
            snapshot_df = snapshot_df.applymap(lambda x: str(
                x) if isinstance(x, (int, decimal.Decimal, float)) else x)
            snapshot_data = snapshot_df.to_dict(orient='records')

            # Pagination
            total_count = pd.read_sql_query(count_query, engine, params=params).iloc[0, 0]
            paginator = Paginator(range(total_count), page_size)

            return { 'data': snapshot_data, 'total': paginator.count }
        except Exception as e:
            print(e.args)
            return { 'data': [], 'total': 0, "error": e.args }
