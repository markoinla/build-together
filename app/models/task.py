from app import db
from datetime import datetime

class Task(db.Model):
    """
    Task model representing a specific task within a sprint
    
    Fields:
    - id: Primary key
    - details: Task details (required)
    - completed: Whether the task is completed (boolean)
    - starred: Whether the task is starred/important (boolean)
    - sprint_id: Foreign key to the associated sprint
    - created_at: Timestamp when the task was created
    - updated_at: Timestamp when the task was last updated
    """
    # Table name
    __tablename__ = 'tasks'
    
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    details = db.Column(db.Text, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    starred = db.Column(db.Boolean, default=False)  # New field to mark tasks as starred/important
    sprint_id = db.Column(db.Integer, db.ForeignKey('sprints.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        """String representation of the Task object"""
        status = 'Completed' if self.completed else 'Pending'
        return f'<Task {self.id} - {status}>'
    
    def to_dict(self):
        """Convert task to dictionary for API responses"""
        return {
            'id': self.id,
            'details': self.details,
            'completed': self.completed,
            'starred': self.starred,  # Include starred field in API responses
            'sprint_id': self.sprint_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
