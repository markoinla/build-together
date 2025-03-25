from app import db
from datetime import datetime
from app.models.issue import Issue
from app.models.task import Task

class Sprint(db.Model):
    """
    Sprint model representing a work period within a project
    
    Fields:
    - id: Primary key
    - name: Sprint name (required)
    - description: Sprint description
    - status: Sprint status (Planned, Active, Completed)
    - project_id: Foreign key to the associated project
    - created_at: Timestamp when the sprint was created
    - updated_at: Timestamp when the sprint was last updated
    - tasks: Relationship to Task model (one-to-many)
    - issues: Relationship to Issue model (one-to-many)
    """
    # Table name
    __tablename__ = 'sprints'
    
    # Status options
    STATUS_PLANNED = 'Planned'
    STATUS_ACTIVE = 'Active'
    STATUS_COMPLETED = 'Completed'
    
    # Valid status values
    VALID_STATUSES = [STATUS_PLANNED, STATUS_ACTIVE, STATUS_COMPLETED]
    
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default=STATUS_PLANNED)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    # One sprint can have many tasks
    tasks = db.relationship('Task', backref='sprint', lazy='dynamic', cascade='all, delete-orphan')
    # One sprint can have many issues
    issues = db.relationship('Issue', backref='sprint', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        """String representation of the Sprint object"""
        return f'<Sprint {self.name} - {self.status}>'
    
    def to_dict(self):
        """Convert sprint to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'project_id': self.project_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
    def get_sorted_tasks(self):
        """
        Get tasks sorted by:
        1. Open tasks first (oldest first)
        2. Closed tasks second (oldest first)
        """
        open_tasks = self.tasks.filter_by(completed=False).order_by(Task.created_at.asc()).all()
        closed_tasks = self.tasks.filter_by(completed=True).order_by(Task.created_at.asc()).all()
        return open_tasks + closed_tasks
    
    def get_sorted_issues(self):
        """
        Get issues sorted by:
        1. Open issues first (oldest first)
        2. Closed issues second (oldest first)
        """
        open_issues = self.issues.filter_by(completed=False).order_by(Issue.created_at.asc()).all()
        closed_issues = self.issues.filter_by(completed=True).order_by(Issue.created_at.asc()).all()
        return open_issues + closed_issues
    
    def to_dict_simple(self):
        """Convert sprint to dictionary without related objects for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'project_id': self.project_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
