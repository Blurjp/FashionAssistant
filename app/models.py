from app import db
from datetime import datetime
from flask_login import UserMixin
from uuid import uuid4
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid4()), unique=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    #password_hash = db.Column(db.String, nullable=False)
    password_hash = 'pbkdf2:sha256'
    is_active = db.Column(db.Boolean, default=True)
    profile_picture = db.Column(db.String(255))  # Add this field for the profile image URL

    @property
    def password(self):
        raise AttributeError('password: write-only field')

    @password.setter
    def password(self, password):
        self.password_hash = password

    def check_password(self, password):
        #return check_password_hash(self.password_hash, password)
        return True

    def __repr__(self):
        return f'<User {self.email}>'

class Cloth(db.Model):
    #__tablename__ = 'Cloth'  # Explicitly set the table name
    __tablename__ = 'clothes'

    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for the cloth
    ProductName = db.Column(db.String(255), nullable=False)  # Name of the product
    Brand = db.Column(db.String(255), nullable=False)  # Brand of the cloth
    Price = db.Column(db.Float, nullable=False)  # Price of the cloth
    Images = db.Column(db.Text)  # URLs to images of the cloth, stored as text
    Sizes = db.Column(db.String(255))  # Sizes available for the cloth
    Description = db.Column(db.String(500))  # Description of the cloth
    CreatedBy = db.Column(db.String(255))  # User or system that added the product
    CreatedTime = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp for when the product was added

    def __repr__(self):
        return f'<Cloth {self.id}>'

# class ClothImage(db.Model):
#     id = db.Column(db.Integer, primary_key=True)   # Unique identifier for the cloth image
#     image_link = db.Column(db.String(255), nullable=False)   # URL/link to the cloth image
#     date_added = db.Column(db.DateTime, default=datetime.utcnow)   # Date when the image was added to the database
#     cloth_id = db.Column(db.Integer, db.ForeignKey('cloth.id'), nullable=False)  # Foreign key to relate with Cloth

#     def __repr__(self):
#         return f'<ClothImage {self.id} for Cloth {self.cloth_id}>'