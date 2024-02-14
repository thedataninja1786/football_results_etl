import requests
import numpy as np
import os
import pandas as pd
from datetime import datetime, timedelta
import json
import time
from configs.api import FootballAPIConfig as Config
import logging

logs_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

logging.basicConfig(filename=f"logs/app-{logs_datetime}.log", level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class FootballAPI:
    def __init__(self):
         self.api_key = Config.API_KEY
         self.host = Config.HOST
         self.base_url = Config.BASE_URL
         self.unicode_mapping = Config.UNICODE_MAPPING
         

    def get_headers(self):
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host":self.host,
        }

    
    def gen_url(self,date):        
        return self.base_url + date


    def get_date_range(self, source_date, window=None):
        if window is None:
            window = Config.DATA_WINDOW

        shift = Config.DATA_SHIFT
        start_date = source_date - timedelta(window + shift)
        end_date = source_date - timedelta(shift)

        dates = pd.date_range(start_date, end_date).strftime(Config.DATE_FORMAT)

        return list(dates)
    

    def get_request(self,date):
        url = self.gen_url(date)
        try:
            response = requests.get(
                                    url,
                                    headers = self.get_headers()
                                    )
            if response.status_code == 200:
                logging.info(f"{self.__class__.__name__} - request for {date} was successful!")
                return response.json()
            else:
                print(f"Failed to retrieve data with status code {response.status_code} - {response.content}")
                logging.critical(f"{self.__class__.__name__} [CRITICAL ERROR] \
                                  - failed to retrieve data with status code {response.status_code} - {response.content}!")
        except Exception as e:
            logging.warning(f"{self.__class__.__name__} - failed to retrieve data for date {date} with exception {e}!")
            print(f"Failed to retrieve data for date {date} with exception {e}!")
        
        return {}
                

    def transform_data(self,data,source_date):
        """ Remove unicode characters from team names"""
        processing_timestamp = source_date.strftime("%Y-%m-%d %H:%M:%S")
        data = json.loads(json.dumps(data).replace('\\', '\\\\'))
        
        try:
            for v in data.values():
                v["processing_timestamp"] = processing_timestamp
                for k in self.unicode_mapping.keys():
                    if k in v["homeTeam"]:
                        v["homeTeam"] = v["homeTeam"].replace(k,self.unicode_mapping[k])
                        v["homeTeam"] = "".join([x for x in v["homeTeam"] if x != "\\"])
                        
                    if k in v["awayTeam"]:
                        v["awayTeam"] = v["awayTeam"].replace(k,self.unicode_mapping[k])
                        v["awayTeam"] = "".join([x for x in v["awayTeam"] if x != "\\"])
        
        except Exception as e:
            logging.error(f"{self.__class__.__name__} - [ERROR] occurred when transforming data!" )

        return data
    

    def get_data(self):
        result_df = pd.DataFrame()
        source_date = datetime.now()
        dates = self.get_date_range(source_date=source_date,window=1)
        for date in dates:
            data = self.get_request(date=date)
            if data:
                num_results = data["api"]["results"]
                data = data["api"]["fixtures"]
                data = self.transform_data(data,source_date=source_date)
                data = pd.DataFrame(data).T
                result_df = result_df.append(data,ignore_index = True)
                if num_results != data.shape[0]:
                    logging.critical(f"{self.__class__.__name__} [CRITICAL ERROR] \
                                     - data received {num_results} != data after processing {data.shape[0]}!")
        
        return result_df

