from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

## configuration of the Data Ingestion config

from networksecurity.entity.config_entity import DataIngestionConfig
from networksecurity.entity.artifact_entity import DataIngestionArtifact
import os
import sys
from typing import List
import numpy as np
import pandas as pd
import pymongo
from sklearn.model_selection import train_test_split
from dotenv import load_dotenv
load_dotenv()

MONGO_DB_URL = os.getenv("MONGO_DB_URL")

class DataIngestion:
    def __init__(self,Data_Ingestion_Config:DataIngestionConfig):
        try:
            self.Data_Ingestion_Config=Data_Ingestion_Config
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def Extract_Data_from_mongo(self):
        try:
            database_name=self.Data_Ingestion_Config.database_name
            collection_name=self.Data_Ingestion_Config.collection_name
            self.mongo_client=pymongo.MongoClient(MONGO_DB_URL)
            collection=self.mongo_client[database_name][collection_name] 

            df=pd.DataFrame(list(collection.find()))

            if "_id" in df.columns.to_list():
                df=df.drop(columns=["_id"],axis=1)
            
            df.replace({"na":np.nan},inplace=True)

            return df

        except Exception as e:
            raise NetworkSecurityException(e,sys)

    def export_data_to_feature_store(self,dataframe:pd.DataFrame):
        try:
            feature_store_path=self.Data_Ingestion_Config.feature_store_file_path
            ##creating folder and store csv
            dir_path=os.path.dirname(feature_store_path)
            os.makedirs(dir_path,exist_ok=True)
            dataframe.to_csv(feature_store_path,index=False,header=True)
            return dataframe
        except Exception as e:
            raise NetworkSecurityException(e,sys)       

    def split_data_as_train_test(self,dataframe:pd.DataFrame):
        try:
            train_set,test_set=train_test_split(
                dataframe,test_size=self.Data_Ingestion_Config.train_test_split_ratio)
            logging.info("Process train test split data begin")
            logging.info("Process train test split data end")
            dir_path=os.path.dirname(self.Data_Ingestion_Config.training_file_path)
            os.makedirs(dir_path,exist_ok=True)
            logging.info("Exporting training data")
            train_set.to_csv(
                self.Data_Ingestion_Config.training_file_path, index=False, header=True
            )
            test_set.to_csv(
                self.Data_Ingestion_Config.testing_file_path, index=False, header=True
            )
        except Exception as e:
            raise NetworkSecurityException(e,sys) 

    def initiate_data_ingestion(self):
        try:
            dataframe=self.Extract_Data_from_mongo()
            dataframe=self.export_data_to_feature_store(dataframe)
            self.split_data_as_train_test(dataframe)
            dataingestionartifact=DataIngestionArtifact(
                trained_file_path=self.Data_Ingestion_Config.training_file_path,
                test_file_path=self.Data_Ingestion_Config.testing_file_path)
            return dataingestionartifact
        except Exception as e:
            raise NetworkSecurityException(e,sys)