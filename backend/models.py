from database import db
from datetime import datetime

class User(db.Model):
    """User model - stores team member information"""
    __tablename__ = 'users'
    
    user_id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    initials = db.Column(db.String(5))
    role = db.Column(db.String(50))
    team = db.Column(db.String(50))
    avatar_url = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    tasks = db.relationship('Task', backref='assignee', lazy='dynamic')
    
    def __repr__(self):
        return f'<User {self.name}>'

class Task(db.Model):
    """Task model - stores all task information"""
    __tablename__ = 'tasks'
    
    task_id = db.Column(db.String(50), primary_key=True)
    task_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False)  # Open, In Progress, Completed, Blocked
    priority = db.Column(db.String(20))  # High, Medium, Low
    project = db.Column(db.String(100))  # Web Platform, Mobile App, API Services
    assigned_to = db.Column(db.String(50), db.ForeignKey('users.user_id'))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    start_date = db.Column(db.DateTime)
    completed_date = db.Column(db.DateTime)
    estimated_hours = db.Column(db.Float)
    tags = db.Column(db.String(200))  # Comma-separated tags
    blocked_reason = db.Column(db.String(200))
    comments = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Task {self.task_name}>'

