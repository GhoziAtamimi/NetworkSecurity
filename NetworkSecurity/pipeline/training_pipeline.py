import os,sys

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.components.data_transformation import DataTransformation
from networksecurity.components.model_trainer import ModelTrainer

from networksecurity.entity.config_entity import (DataIngestionConfig,DataValidationConfig,
                                                  DataTransformationConfig,ModelTrainerConfig,TrainingPipelineConfig)
from networksecurity.entity.artifact_entity import (DataIngestionArtifact,DataValidationArtifact,
                                                    DataTransformationArtifact,ModelTrainerArtifact)
from networksecurity.constants.training_pipeline import TRAINING_BUCKET_NAME,SAVED_MODEL_DIR
from networksecurity.cloud.s3_syncer import S3Sync

class Trainingpipeline:
    def __init__(self):
        self.training_pipeline_config=TrainingPipelineConfig()
        

    def StartDataIngestion(self):
        try:
            self.data_ingestion_config=DataIngestionConfig(training_pipeline_config=self.training_pipeline_config)
            logging.info("Start Data Ingestion")
            data_ingestion=DataIngestion(Data_Ingestion_Config=self.data_ingestion_config)
            data_ingestion_artifact=data_ingestion.initiate_data_ingestion()
            logging.info(f"Data Ingestion completed and artifact : {data_ingestion_artifact}")
            return data_ingestion_artifact
        except Exception as e:
            raise NetworkSecurityException(e,sys)
    
    def StartDataValidation(self,data_ingestion_artifact:DataIngestionArtifact):
        try:
            self.data_validation_config=DataValidationConfig(training_pipeline_config=self.training_pipeline_config)
            logging.info("Start Data Validation")
            data_validation=DataValidation(data_validation_config=self.data_validation_config,
                                           data_ingestion_artifact=data_ingestion_artifact)
            data_validation_artifact=data_validation.iniate_data_validation()
            logging.info(f"Data Validation completed and artifact : {data_validation_artifact}")
            return data_validation_artifact
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def StartDataTransformation(self,data_validation_artifact:DataValidationArtifact):
        try:
            self.data_transformation_config=DataTransformationConfig(training_pipeline_config=self.training_pipeline_config)
            logging.info("Start Data Transformation")
            data_transformation=DataTransformation(data_trasformation_config=self.data_transformation_config,
                                                   data_validation_artifact=data_validation_artifact)
            data_transformation_artifact=data_transformation.initiate_data_transformation()
            logging.info(f"Data Transformation completed and artifact : {data_transformation_artifact}")
            return data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    def StartModelTrainer(self,data_transformation_artifact:DataTransformationArtifact)->ModelTrainerArtifact:
        try:
            self.model_trainer_config=ModelTrainerConfig(training_pipeline_config=self.training_pipeline_config)
            logging.info("Start Model Training")
            model_trainer=ModelTrainer(data_transformation_artifact=data_transformation_artifact,
                                       model_trainer_config=self.model_trainer_config)
            model_trainer_artifact=model_trainer.initiate_model_trainer()
            logging.info(f"Model Training completed and artifact : {model_trainer_artifact}")
            return model_trainer_artifact
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    ## local artifact is going to s3 bucket    
    def sync_artifact_dir_to_s3(self):
        try:
            aws_bucket_url = f"s3://{TRAINING_BUCKET_NAME}/artifact/{self.training_pipeline_config.timestamp}"
            self.s3_sync.sync_folder_to_s3(folder = self.training_pipeline_config.artifact_dir,aws_bucket_url=aws_bucket_url)
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        
    ## local final model is going to s3 bucket 
        
    def sync_saved_model_dir_to_s3(self):
        try:
            aws_bucket_url = f"s3://{TRAINING_BUCKET_NAME}/final_model/{self.training_pipeline_config.timestamp}"
            self.s3_sync.sync_folder_to_s3(folder = self.training_pipeline_config.model_dir,aws_bucket_url=aws_bucket_url)
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        

    def run_pipeline(self):
        try:
            data_ingestion_artifact=self.StartDataIngestion()
            data_validation_artifact=self.StartDataValidation(data_ingestion_artifact=data_ingestion_artifact)
            data_transformation_artifact=self.StartDataTransformation(data_validation_artifact=data_validation_artifact)
            model_trainer_artifact=self.StartModelTrainer(data_transformation_artifact=data_transformation_artifact)
            
            self.sync_artifact_dir_to_s3()
            self.sync_saved_model_dir_to_s3()

            return model_trainer_artifact
        except Exception as e:
            raise NetworkSecurityException(e,sys)