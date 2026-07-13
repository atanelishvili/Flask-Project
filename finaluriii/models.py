from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), default='Visitor') 
    phone = db.Column(db.String(50), nullable=True)

    properties = db.relationship('Property', backref='owner', lazy=True)
    favorites = db.relationship('Favorite', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)       
    deal_type = db.Column(db.String(50), nullable=False)  
    price = db.Column(db.Float, nullable=False)
    area_sqm = db.Column(db.Float, nullable=False)
    rooms = db.Column(db.Integer, nullable=False)
    floor = db.Column(db.Integer, nullable=True)
    total_floors = db.Column(db.Integer, nullable=True)
    city = db.Column(db.String(100), nullable=False)
    district = db.Column(db.String(100), nullable=True)
    address = db.Column(db.String(255), nullable=False)
    lat = db.Column(db.Float, nullable=True)
    lon = db.Column(db.Float, nullable=True)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    views = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=30))

    images = db.relationship('PropertyImage', backref='property', lazy=True, cascade="all, delete-orphan")
    contacts = db.relationship('ContactRequest', backref='property', lazy=True, cascade="all, delete-orphan")

class PropertyImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    image_url = db.Column(db.Text, nullable=False)
    order = db.Column(db.Integer, default=1)

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)

class ContactRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)