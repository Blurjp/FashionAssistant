import pandas as pd
from datetime import datetime
import validators
import logging
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, Text, DateTime, select
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker
from config import DevelopmentConfig  # Ensure config.py contains your configurations
import chardet  # Import chardet to detect file encoding
from tqdm import tqdm
import numpy as np
import boto3  # AWS SDK for Python
import requests, uuid

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize configuration using your DevelopmentConfig
config = DevelopmentConfig()

# Create an engine
engine = create_engine(config.SQLALCHEMY_DATABASE_URI, echo=config.DEBUG)

# Initialize MetaData and bind the engine
metadata = MetaData()
metadata.bind = engine

# Define the table schema using SQLAlchemy
#products_table = Table('Cloth', metadata,
products_table = Table('clothes', metadata,
                       Column('ProductName', String(255), nullable=False),
                       Column('Brand', String(255), nullable=False),
                       Column('Price', Float, nullable=False),
                       Column('Images', Text),
                       Column('Sizes', String(255)),
                       Column('Description', Text),
                       Column('CreatedBy', String(255)),
                       Column('CreatedTime', DateTime, default=func.current_timestamp())
                       )

# Ensure table exists
metadata.create_all(engine)

# Define headers to mimic a browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
    'Referer': 'https://www.google.com/',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
}

# Initialize AWS S3 and CloudFront clients
s3_client = boto3.client(
    's3',
    aws_access_key_id=config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
    region_name=config.AWS_REGION_NAME
)
cloudfront_domain = config.CLOUDFRONT_DOMAIN
s3_bucket = config.S3_CLOTH_IMAGE_BUCKET_NAME

def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    return result['encoding']

# Upload images to S3 and return CloudFront URLs
def upload_images_to_s3(url_list):
    cloudfront_urls = []
    print(url_list)
    for url in url_list.split(',')[:2]:
        if validators.url(url):
            # Download the image content
            print('Download the image content')
            #image_name = url.split('/')[-1]
            image_name = f"{uuid.uuid4()}.jpg"
            #response = requests.get(url)
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                # Upload to S3
                print('Upload to S3')
                s3_key = f"images/{image_name}"
                s3_client.put_object(Bucket=s3_bucket, Key=s3_key, Body=response.content)
                # Generate CloudFront URL
                print('Generate CloudFront URL')
                cloudfront_url = f"https://{cloudfront_domain}/{s3_key}"
                cloudfront_urls.append(cloudfront_url)
                logging.info(f"cloudfront_url: {cloudfront_url}")
            else:
                logging.error(f"Failed to download image: {url}")
        else:
            error_message = f"Invalid URL detected: {url}"
            logging.error(error_message)
            #raise ValueError(error_message)
    return ','.join(cloudfront_urls)


# Read and preprocess the CSV file
def read_and_preprocess_data(file_path):
    encoding = detect_encoding(file_path)  # Detect the encoding of the file
    logging.info(f"Detected file encoding: {encoding}")
    try:
        data = pd.read_csv(file_path, encoding=encoding)
        data.columns = ['ProductName', 'Brand', 'Price', 'Sizes', 'Images', 'Description']
        print(data['ProductName'])
        #data['Images'] = data['Images'].apply(upload_images_to_s3)
        data['Images'] = data['Images']
        # image_urls = []
        # print(data['Images'])
        # for image in data['Images']:
        #     image_urls.append(upload_images_to_s3(image))
        # data['Images'] = image_urls
        logging.info('finish apply upload_images_to_s3')
        print(data['ProductName'])
        data['CreatedBy'] = 'System'
        data['CreatedTime'] = datetime.now()
        return data
    except Exception as e:
        logging.error(f"Failed to read or preprocess data: {e}")
        #raise

# Validate and format URLs
# def validate_urls(url_list):
#     valid_urls = []
#     for url in url_list.split(','):
#         if validators.url(url):
#             valid_urls.append(url)
#         else:
#             error_message = f"Invalid URL detected: {url}"
#             logging.error(error_message)
#             raise ValueError(error_message)
#     return ','.join(valid_urls)

# Insert data into the database
def insert_data(df):
    if df is None or df.empty:
        logging.error("The DataFrame is empty or invalid.")
        return
    
    Session = sessionmaker(bind=engine)
    session = Session()
    existing_products = {name[0] for name in session.execute(select(products_table.c.ProductName))}
    
    try:
        logging.info("Start to insert into the database.")
        for _, row in tqdm(df.iterrows(), total=df.shape[0], desc="Inserting records"):
            row = row.replace({np.nan: None})  # Replacing NaN with None, which translates to SQL NULL            

            # if row['ProductName'] in existing_products:
            #     logging.info(f"Skipping duplicate: {row['ProductName']}")
            #     continue
            # Correctly using insert method
            insert_stmt = products_table.insert().values(
                ProductName=row['ProductName'],
                Brand=row['Brand'],
                Price=row['Price'],
                Images=row['Images'],
                Sizes=row['Sizes'],
                Description=row['Description'],
                CreatedBy=row['CreatedBy'],
                CreatedTime=row['CreatedTime']
            )
            session.execute(insert_stmt)  # Executing the insert statement
        session.commit()
        logging.info("Data successfully inserted into the database.")
    except Exception as e:
        session.rollback()
        logging.error(f"An error occurred while inserting data: {e}")
        #raise
    finally:
        session.close()


if __name__ == "__main__":
    try:
        #file_path = 'net-a-porter.csv'
        file_path = 'farfetch_test.csv'
        data = read_and_preprocess_data(file_path)
        logging.info('finish read_and_preprocess_data')
        insert_data(data)
    except Exception as e:
        logging.error(f"Execution halted due to an error: {e}")
