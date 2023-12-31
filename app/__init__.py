from flask import Flask
from flask_login import LoginManager
import os
from flask_migrate import Migrate
from config import DevelopmentConfig, ProductionConfig, TestingConfig
from flask_sqlalchemy import SQLAlchemy
import boto3

app = Flask(__name__)

# Load the appropriate configuration
if os.environ.get('FLASK_ENV') == 'production':
    app.config.from_object(ProductionConfig)
elif os.environ.get('FLASK_ENV') == 'testing':
    app.config.from_object(TestingConfig)
else:
    app.config.from_object(DevelopmentConfig)

# Initialize the SQLAlchemy instance
db = SQLAlchemy(app)

login_manager = LoginManager(app)  # Initialize the LoginManager instance
login_manager.login_view = 'routes.login'  # Set the view function name for the login page

app.secret_key = os.urandom(24)
#print(app.config['AWS_ACCESS_KEY_ID'])
#print(app.config['AWS_SECRET_ACCESS_KEY'])

image_processing_service_url = app.config['IMAGE_PROCESSING_SERVICE_URL']

# Create the S3 client
s3 = boto3.client('s3',
                  aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
                  aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY'],
                  region_name=app.config['AWS_REGION_NAME'])

profileImageS3Bucket = app.config['S3_PROFILE_IMAGE_BUCKET_NAME']

migrate = Migrate(app, db)

from app import models

def create_app():
    from app.routes import routes
    app.register_blueprint(routes)

    @login_manager.user_loader
    def load_user(user_id):
        return models.User.query.get(user_id)

    return app

app = create_app()
