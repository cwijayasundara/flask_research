from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# Create db model for bucket list items
class BucketListItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    completion_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    # Add a foreign key for the user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # Add a foreign key for the bucket list group (collaboration feature)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=True)


# Create db model for users
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)  # In a real app, you should hash passwords
    email = db.Column(db.String(100), nullable=False, unique=True)
    bucket_list_items = db.relationship('BucketListItem', backref='user', lazy=True)


# Create db model for bucket list groups (for collaboration feature)
class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    bucket_list_items = db.relationship('BucketListItem', backref='group', lazy=True)
