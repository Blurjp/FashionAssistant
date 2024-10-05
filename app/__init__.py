from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth
import boto3
import os
from config import DevelopmentConfig, ProductionConfig, TestingConfig

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
oauth = OAuth()

# Make s3 and other variables global
s3 = None
google = None
profileImageS3Bucket = None
image_processing_service_url = None

def create_app():
    global s3, profileImageS3Bucket, image_processing_service_url, google

    app = Flask(__name__)

    # Load the appropriate configuration
    if os.environ.get('FLASK_ENV') == 'production':
        app.config.from_object(ProductionConfig)
    elif os.environ.get('FLASK_ENV') == 'testing':
        app.config.from_object(TestingConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    # Initialize extensions with the app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'routes.login'
    migrate.init_app(app, db)
    oauth.init_app(app)

    app.secret_key = os.urandom(24)

    # OAuth registration for Google
    google = oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        #authorize_url='https://accounts.google.com/o/oauth2/auth',
        #authorize_params=None,
        #access_token_url='https://accounts.google.com/o/oauth2/token',
        #access_token_params=None,
        client_kwargs={'scope': 'openid profile email'},
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration'  # Ensure metadata URL is correct
    )

    # Create the S3 client (making it globally available)
    s3 = boto3.client('s3',
                      aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
                      aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY'],
                      region_name=app.config['AWS_REGION_NAME'])

    # Set S3 profile image bucket name and image processing service URL globally
    profileImageS3Bucket = app.config['S3_PROFILE_IMAGE_BUCKET_NAME']
    image_processing_service_url = app.config['IMAGE_PROCESSING_SERVICE_URL']

    # Import models
    from app import models

    # Register the routes blueprint
    from app.routes import routes
    app.register_blueprint(routes)

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return models.User.query.get(user_id)

    return app
