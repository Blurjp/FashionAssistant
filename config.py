import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    S3_REGION_NAME = 'us-east-1'

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///development.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    S3_GENERATED_IMAGE_BUCKET_NAME = 'dev-fashion-assistant-user-generated-image-bucket'

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///production.db'  # Change to the appropriate production database URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    S3_GENERATED_IMAGE_BUCKET_NAME = 'prod-fashion-assistant-user-generated-image-bucket'

class TestingConfig(Config):
    TESTING = True
    DEBUG = True
