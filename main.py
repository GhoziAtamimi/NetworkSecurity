from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.components.data_transformation import DataTransformation
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.entity.config_entity import DataIngestionConfig,TrainingPipelineConfig,DataValidationConfig,DataTransformationConfig

import sys

if __name__=="__main__":
    try:
        trainingpipelineconfig=TrainingPipelineConfig()
        dataingestionconfig=DataIngestionConfig(training_pipeline_config=trainingpipelineconfig)
        data_ingestion=DataIngestion(Data_Ingestion_Config=dataingestionconfig)
        logging.info("Inititate Data Ingestion")
        dataingestionartifact=data_ingestion.initiate_data_ingestion()
        logging.info("Data ingestion completed")
        print(dataingestionartifact)
        logging.info("Initiate Data validation")
        datavalidationconfig=DataValidationConfig(training_pipeline_config=trainingpipelineconfig)
        data_validation=DataValidation(data_ingestion_artifact=dataingestionartifact,data_validation_config=datavalidationconfig)
        datavalidationartifact=data_validation.iniate_data_validation()
        logging.info("Data validation completed")
        print(datavalidationartifact)
        logging.info("Initiate Data Transformation")
        data_transformation_config=DataTransformationConfig(training_pipeline_config=trainingpipelineconfig)
        data_transformation=DataTransformation(data_validation_artifact=datavalidationartifact,data_trasformation_config=data_transformation_config)
        data_transformation_artifact=data_transformation.initiate_data_transformation()
        logging.info("Data transformation completed")
        print(data_transformation_artifact)
    except Exception as e:
            raise NetworkSecurityException(e,sys)