from app import db
from datetime import datetime
from app.models.sprint import Sprint

class Project(db.Model):
    """
    Project model representing an AI coding project
    
    Fields:
    - id: Primary key
    - name: Project name (required)
    - description: Project description and goals
    - requirements: Project requirements
    - implementation_details: Project implementation details
    - created_at: Timestamp when the project was created
    - updated_at: Timestamp when the project was last updated
    - sprints: Relationship to Sprint model (one-to-many)
    """
    # Table name
    __tablename__ = 'projects'
    
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    requirements = db.Column(db.Text, nullable=True)
    implementation_details = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    # One project can have many sprints
    sprints = db.relationship('Sprint', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        """String representation of the Project object"""
        return f'<Project {self.name}>'
    
    def get_sorted_sprints(self):
        """Returns a list of sprints sorted by status priority (Active, Planned, Completed)"""
        from app.models import Sprint
        
        # Define the status priority for sorting
        status_priority = {
            Sprint.STATUS_ACTIVE: 0,
            Sprint.STATUS_PLANNED: 1,
            Sprint.STATUS_COMPLETED: 2
        }
        
        # Get all sprints for this project and sort them by status priority
        return sorted(self.sprints.all(), key=lambda sprint: status_priority.get(sprint.status, 3))
    
    def get_sprint_count(self):
        """Returns the total number of sprints for this project"""
        return self.sprints.count()
    
    def to_dict(self):
        """Convert project to dictionary for API responses"""
        # Define a custom sorting function for sprints based on status priority
        from app.models import Sprint
        status_priority = {
            Sprint.STATUS_ACTIVE: 0,
            Sprint.STATUS_PLANNED: 1,
            Sprint.STATUS_COMPLETED: 2
        }
        
        # Get all sprints for this project
        all_sprints = self.sprints.all()
        
        # Sort sprints by status priority
        sorted_sprints = sorted(all_sprints, key=lambda sprint: status_priority.get(sprint.status, 3))
        
        # Convert to dictionary
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'requirements': self.requirements,
            'implementation_details': self.implementation_details,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'sprint_count': self.get_sprint_count(),
            'sprints': [sprint.to_dict() for sprint in sorted_sprints]
        }
        
    def to_dict_simple(self):
        """Convert project to dictionary without related objects for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'requirements': self.requirements,
            'implementation_details': self.implementation_details,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
