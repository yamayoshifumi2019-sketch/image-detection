"""
models.py - Database Models

This file defines the database tables using Flask-SQLAlchemy.
We have two models:
1. User - stores user account information
2. Image - stores uploaded image information
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

# Create SQLAlchemy instance
# This will be initialized with the Flask app in app.py
db = SQLAlchemy()


class User(UserMixin, db.Model):
    """
    User model for storing user account data.

    UserMixin provides default implementations for:
    - is_authenticated: returns True if user is logged in
    - is_active: returns True if account is active
    - is_anonymous: returns False for regular users
    - get_id(): returns the user ID as a string
    """
    __tablename__ = 'users'

    # Primary key - unique identifier for each user
    id = db.Column(db.Integer, primary_key=True)

    # Username - must be unique, used for login
    username = db.Column(db.String(80), unique=True, nullable=False)

    # Password hash - we never store plain passwords!
    password_hash = db.Column(db.String(200), nullable=False)

    # Relationship: one user can have many images
    # backref='owner' means we can access image.owner to get the user
    images = db.relationship('Image', backref='owner', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'


class Image(db.Model):
    """
    Image model for storing uploaded image information.

    Each image belongs to one user (foreign key relationship).
    We store both the original filename and the detected filename.
    """
    __tablename__ = 'images'

    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Original filename (as uploaded by user)
    original_filename = db.Column(db.String(200), nullable=False)

    # Stored filename (unique name we generate to avoid conflicts)
    stored_filename = db.Column(db.String(200), nullable=False)

    # Detected filename (image with bounding boxes drawn)
    detected_filename = db.Column(db.String(200), nullable=False)

    # Detection results (stored as comma-separated string for simplicity)
    # Example: "person, car, dog"
    detection_results = db.Column(db.Text, nullable=True)

    # Upload timestamp
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign key - links this image to a user
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return f'<Image {self.original_filename}>'
