import psycopg2
from pandas import DataFrame
from psycopg2 import sql
from core.configures_home import Config
from .base_engine import BaseEngine


class PgSqlEngine(BaseEngine):

    def __init__(self, config: Config):
        super().__init__(config)
        self.host = self.config.DB_CONN.get("host")
        self.port = self.config.DB_CONN.get("port")
        self.dbname = config.DB_CONN.get("dbname")
        self.user = config.DB_CONN.get("user")
        self.password = config.DB_CONN.get("password")

        self.db_conn = psycopg2.connect(
            host=self.host,
            port=self.port,
            dbname=self.dbname,
            user=self.user,
            password=self.password,
        )

    def save_df(
            self,
            sql_query: str,
            df_source: DataFrame,
            execute_func: callable
    ):
        with self.db_conn.cursor() as cursor:
            insert_query = psycopg2.sql.SQL(sql_query)
            for _, row in df_source.iterrows():
                result = ()
                try:
                    result = execute_func(_, row)
                    cursor.execute(insert_query, result)
                except Exception as e:
                    print(f"Error: {e}")
                self.db_conn.commit()
