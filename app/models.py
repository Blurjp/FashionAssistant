from app import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    profile_picture = db.Column(db.String(255))  # Add this field for the profile image URL

    @property
    def password(self):
        raise AttributeError('password: write-only field')

    @password.setter
    def password(self, password):
        self.password_hash = password

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'

class Cloth(db.Model):
    id = db.Column(db.Integer, primary_key=True)   # Unique identifier for the cloth
    category = db.Column(db.String(100), nullable=False)  # e.g. 'shirt', 'trouser', 'dress'
    price = db.Column(db.Float, nullable=False)   # Price of the cloth
    store = db.Column(db.String(120), nullable=False)   # Store where the cloth is available
    description = db.Column(db.String(500))   # Description of the cloth
    date_added = db.Column(db.DateTime, default=datetime.utcnow)   # Date when the cloth was added to the database

    # Relationship with ClothImage model
    images = db.relationship('ClothImage', backref='cloth', lazy=True)

    def __repr__(self):
        return f'<Cloth {self.id} - {self.category} from {self.store}>'

class ClothImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)   # Unique identifier for the cloth image
    image_link = db.Column(db.String(255), nullable=False)   # URL/link to the cloth image
    date_added = db.Column(db.DateTime, default=datetime.utcnow)   # Date when the image was added to the database
    cloth_id = db.Column(db.Integer, db.ForeignKey('cloth.id'), nullable=False)  # Foreign key to relate with Cloth

    def __repr__(self):
        return f'<ClothImage {self.id} for Cloth {self.cloth_id}>'