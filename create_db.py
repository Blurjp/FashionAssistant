import os
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean, TIMESTAMP, Float, Text
from sqlalchemy.sql import func
from config import DevelopmentConfig  # Assuming config.py contains your configurations

# Set the environment based on your current mode
config = DevelopmentConfig()  # Switch to ProductionConfig or TestingConfig as needed

# Establish the database connection using SQLAlchemy
engine = create_engine(config.SQLALCHEMY_DATABASE_URI, echo=True)  # 'echo=True' for SQL logging

metadata = MetaData()

# Define the Users table (as previously defined)
# users = Table('Users', metadata,
#               Column('id', Integer, primary_key=True, autoincrement=True),
#               Column('name', String(100), nullable=False),
#               Column('email', String(100), unique=True, nullable=False),
#               Column('password_hash', String(255), nullable=False),
#               Column('is_active', Boolean, default=True),
#               Column('created_at', TIMESTAMP, default=func.current_timestamp())
#               )

# Define the Cloth table
cloths = Table('Cloth', metadata,
               Column('id', Integer, primary_key=True, autoincrement=True),
               Column('ProductName', String(255), nullable=False),
               Column('Brand', String(255), nullable=False),
               Column('Price', Float, nullable=False),
               Column('Images', Text),
               Column('Sizes', String(255)),
               Column('Description', String(500)),
               Column('CreatedBy', String(255)),
               Column('CreatedTime', TIMESTAMP, default=func.current_timestamp())
               )

# Create the tables in the database
metadata.create_all(engine)
