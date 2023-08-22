import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_REGION_NAME = 'us-east-1'
    IMAGE_PROCESSING_SERVICE_URL = "http://192.168.1.118:5000/api/process_image"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def get_database_url(host):
        return 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8mb4'.format(
            os.environ.get('db_username'),
            os.environ.get('db_password'),
            host,
            3306,
            'user_datastore'
        )

class DevelopmentConfig(Config):
    DEBUG = True
    S3_GENERATED_IMAGE_BUCKET_NAME = 'dev-fashion-assistant-user-generated-image-bucket'
    S3_PROFILE_IMAGE_BUCKET_NAME = 'dev-fashion-assistant-user-image-profile-bucket'
    SQLALCHEMY_DATABASE_URI = Config.get_database_url('dev-newfashion-database.c71kw1ld7wzd.us-east-2.rds.amazonaws.com')

class ProductionConfig(Config):
    DEBUG = False
    S3_GENERATED_IMAGE_BUCKET_NAME = 'prod-fashion-assistant-user-generated-image-bucket'
    S3_PROFILE_IMAGE_BUCKET_NAME = 'prod-fashion-assistant-user-image-profile-bucket'
    SQLALCHEMY_DATABASE_URI = Config.get_database_url('prod-newfashion-database.c71kw1ld7wzd.us-east-2.rds.amazonaws.com')

class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = Config.get_database_url('test-newfashion-database.c71kw1ld7wzd.us-east-2.rds.amazonaws.com')
