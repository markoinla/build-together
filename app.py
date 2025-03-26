"""
Main application entry point for the BTG project management application.

This file creates the Flask application instance and sets up the database.
It also provides a CLI command for initializing the database.
"""
from app import create_app, db
from app.models import Project, Sprint, Task, Issue
from flask import render_template
import click
from datetime import datetime

# Create the application instance
app = create_app()

# Add current year to template context
@app.context_processor
def inject_now():
    """
    Inject the current year into all templates for the footer copyright
    
    Returns:
        dict: A dictionary containing the current year
    """
    return {'now': datetime.utcnow()}

# CLI command to initialize the database
@app.cli.command('init-db')
def init_db():
    """
    Initialize the database by creating all tables.
    
    This command drops all existing tables and creates new ones.
    """
    click.echo('Initializing the database...')
    db.drop_all()
    db.create_all()
    click.echo('Database initialized!')

# CLI command to create sample data
@app.cli.command('create-sample-data')
def create_sample_data():
    """
    Create sample data for testing the application.
    
    This command creates a sample project with sprints, tasks, and issues.
    """
    click.echo('Creating sample data...')
    
    # Create a sample project
    project = Project(
        name='Sample AI Project',
        description='This is a sample AI project for testing the application.',
        requirements='- Python 3.8+\n- TensorFlow 2.0+\n- PyTorch 1.8+'
    )
    db.session.add(project)
    db.session.commit()
    
    # Create sample sprints
    sprint1 = Sprint(
        name='Sprint 1: Planning',
        description='Initial planning and requirements gathering',
        status='Completed',
        project_id=project.id
    )
    
    sprint2 = Sprint(
        name='Sprint 2: Development',
        description='Core development of the AI model',
        status='Active',
        project_id=project.id
    )
    
    sprint3 = Sprint(
        name='Sprint 3: Testing',
        description='Testing and validation of the AI model',
        status='Planned',
        project_id=project.id
    )
    
    db.session.add_all([sprint1, sprint2, sprint3])
    db.session.commit()
    
    # Create sample tasks
    tasks = [
        Task(details='Define project scope', completed=True, sprint_id=sprint1.id),
        Task(details='Gather requirements', completed=True, sprint_id=sprint1.id),
        Task(details='Create project timeline', completed=True, sprint_id=sprint1.id),
        
        Task(details='Set up development environment', completed=True, sprint_id=sprint2.id),
        Task(details='Implement core AI algorithms', completed=False, sprint_id=sprint2.id),
        Task(details='Create data pipeline', completed=False, sprint_id=sprint2.id),
        
        Task(details='Create test cases', completed=False, sprint_id=sprint3.id),
        Task(details='Perform unit testing', completed=False, sprint_id=sprint3.id),
        Task(details='Validate model accuracy', completed=False, sprint_id=sprint3.id)
    ]
    
    # Create sample issues
    issues = [
        Issue(details='Unclear requirements for model accuracy', completed=True, sprint_id=sprint1.id),
        Issue(details='Missing data for training', completed=False, sprint_id=sprint2.id),
        Issue(details='Performance issues with large datasets', completed=False, sprint_id=sprint2.id)
    ]
    
    db.session.add_all(tasks)
    db.session.add_all(issues)
    db.session.commit()
    
    click.echo('Sample data created!')

if __name__ == '__main__':
    """
    Run the application when executed directly.
    
    This is used for development. In production, use a WSGI server like Gunicorn.
    """
    from config import Config
    app.run(debug=True, port=Config.PORT)
