from app import db
from datetime import datetime

class Issue(db.Model):
    """
    Issue model representing a problem or bug within a sprint
    
    Fields:
    - id: Primary key
    - details: Issue details (required)
    - completed: Whether the issue is resolved (boolean)
    - starred: Whether the issue is starred/important (boolean)
    - sprint_id: Foreign key to the associated sprint
    - created_at: Timestamp when the issue was created
    - updated_at: Timestamp when the issue was last updated
    """
    # Table name
    __tablename__ = 'issues'
    
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    details = db.Column(db.Text, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    starred = db.Column(db.Boolean, default=False)  # New field to mark issues as starred/important
    sprint_id = db.Column(db.Integer, db.ForeignKey('sprints.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        """String representation of the Issue object"""
        status = 'Resolved' if self.completed else 'Open'
        return f'<Issue {self.id} - {status}>'
    
    def to_dict(self):
        """Convert issue to dictionary for API responses"""
        return {
            'id': self.id,
            'details': self.details,
            'completed': self.completed,
            'starred': self.starred,  # Include starred field in API responses
            'sprint_id': self.sprint_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
