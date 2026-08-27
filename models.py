from app import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    
    # Login details
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # NEW: Profile picture file name
    profile_picture = db.Column(db.String(255), default="default.png")
    
    name = db.Column(db.String(100), default="New User")
    occupation = db.Column(db.String(100), default="Not specified")
    age = db.Column(db.Integer, default=0)
    goal_score = db.Column(db.Integer, default=0)
    days_active = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    entries = db.relationship('BehavioralEntry', backref='user', lazy=True)


class BehavioralEntry(db.Model):
    __tablename__ = 'behavioral_entries'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    entry_type = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    recurring_frequency = db.Column(db.String(50))
    impact_on_goals = db.Column(db.String(50))
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)