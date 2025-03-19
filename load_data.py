import pandas as pd
import sqlite3
import os
from typing import Optional
from configs.api import SchemaConfigs as Config
import logging 
from datetime import datetime

logs_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

logging.basicConfig(filename=f"logs/app - {logs_datetime}.log", level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class DataLoader():
    def __init__(self):
        self.db_name = Config.DATABASE_NAME
        self.table_name = Config.TABLE_NAME
        self.table_data = Config.TABLE_DATA
        self.conn = None

    def connect(self) -> None:
        try:
            if os.path.exists(self.db_name):
                logging.info(f"{self.__class__.__name__} [INFO] - connected to database: {self.db_name}")
            else:
                logging.info(f"{self.__class__.__name__} [INFO] - {self.db_name} does not exist, and has been created!")            
            self.conn = sqlite3.connect(self.db_name)
        except Exception as e:
            logging.error(f"{self.__class__.__name__} - [ERROR] {e} occurred when trying to connect to {self.db_name}!")
    

    def write_data(self,data_df:pd.DataFrame,write_method:Optional[str]="upsert") -> None:
        if write_method == "replace":
            data_df.to_sql(self.table_name, self.conn, if_exists='replace', index=False)
        elif write_method == "append":
            data_df.to_sql(self.table_name, self.conn, if_exists='append', index=False)
        elif write_method == "upsert":

            update_columns = [c for c in data_df.columns if c not in ['fixture_id', 'event_timestamp']]
            upsert_query =      f"""
                                    INSERT INTO {self.table_name} ({', '.join(data_df.columns)})
                                    VALUES ({', '.join(['?' for _ in data_df.columns])})
                                    ON CONFLICT(fixture_id, event_timestamp) DO UPDATE SET
                                    {', '.join([f"{col}=EXCLUDED.{col}" for col in update_columns])};
                                """ 
            data_tuples = list(data_df.itertuples(index=False, name=None))
            
        else:
            logging.error(f"{self.__class__.__name__} [ERROR] when trying to write data with {write_method} parameter! ")
            raise NotImplementedError(f"{write_method} is not implemented!")            

        try:
            cursor = self.conn.cursor()
            cursor.executemany(upsert_query, data_tuples)
            self.conn.commit()
            print((f"Data upserted successfully into {self.table_name}."))
            logging.info(f"{self.__class__.__name__} [INFO] - data upserted successfully into table {self.table_name}.")
        except Exception as e:
            logging.critical(f"{self.__class__.__name__} [CRITICAL ERROR] {e}")
            print(f"A critical error has occurred: {e}")
        finally:
            cursor.close()


    def create_table(self) -> None:
        try:
            cursor = self.conn.cursor()
            # Check if the table exists
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{self.table_name}'")
            exists = cursor.fetchone()

            if not exists:
                columns = ', '.join([f"{column_name} {column_type}" for column_name, column_type in self.table_data.items()])
                create_table_query = f"CREATE TABLE {self.table_name} ({columns}, UNIQUE(fixture_id, event_timestamp))"
                cursor.execute(create_table_query)
                self.conn.commit()
                logging.info((f"{self.__class__.__name__} - table {self.table_name} created successfully."))
                print(f"Table {self.table_name} created successfully.")
            else:
                logging.info(f"{self.__class__.__name__} [INFO] - table {self.table_name} already exists.")
                print(f"{self.__class__.__name__} - table {self.table_name} already exists.")
        except Exception as e:
            logging.error(f"{self.__class__.__name__} [ERROR] - {e} when trying to create table {self.table_name}!")
            print(f"The following error has occurred {e} when trying to create table {self.table_name}!")
        finally:
            cursor.close()


    def drop_table(self, table_name:str) -> None:
        try:
            cursor = self.conn.cursor()
            drop_query = f"DROP TABLE IF EXISTS {table_name}"
            cursor.execute(drop_query)
            self.conn.commit()
            logging.info((f"{self.__class__.__name__} - table {table_name} has been dropped successfully."))
            print(f"Table {table_name} has been dropped successfully.")
        except Exception as e:
            logging.error(f"{self.__class__.__name__} [ERROR] while dropping the table {table_name}: {e}")
        finally:
            cursor.close()

        
    def close_connection(self) -> None:
        if self.conn:
            self.conn.close()
            logging.info(f"{self.__class__.__name__} [INFO] - Connection to {self.db_name} closed.")
        else:
            print("No open connection!")

    def query(self,q:str) -> pd.DataFrame:
        with sqlite3.connect(self.db_name) as conn:
            return pd.read_sql(q,con = conn)