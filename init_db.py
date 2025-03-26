"""
Script to initialize the database and create sample data.

This script can be used to reset the database or just add sample data.
WARNING: Using --reset will drop all existing tables and data!
"""
import argparse
from app import create_app, db
from app.models import Project, Sprint, Task, Issue

def init_db(reset=False):
    """Initialize the database and optionally add sample data.
    
    Args:
        reset (bool): If True, drop all tables before creating new ones.
    """
    # Create the application instance
    app = create_app()

    with app.app_context():
        if reset:
            print('WARNING: Resetting the database! All data will be lost!')
            db.drop_all()
            db.create_all()
            print('Database reset and initialized!')
        
        print('Creating sample data...')
        
        # Check if sample project already exists
        if Project.query.filter_by(name='Sample Project: Build Together App').first() is None:
            # Create a sample project
            project = Project(
                name='Sample Project: Build Together App',
                description='A lightweight, self-hosted project management tool built for AI+Human collaboration with vibe coding in mind.',
                requirements='- Python 3.9+ environment\n- Flask web framework with SQLAlchemy ORM\n- Modern UI with Tailwind CSS and DaisyUI\n- MCP (Model Context Protocol) integration for AI coding assistants\n- RESTful API endpoints for all project management functions\n- Configurable port settings to avoid conflicts (default: 3149)\n- Markdown support for rich text descriptions\n- Database migration support for schema evolution',
                implementation_details='## Architecture\n- Flask-based web application with SQLite database\n- Model-View-Controller (MVC) pattern\n- RESTful API with JSON responses\n- HTMX for dynamic UI updates without full page reloads\n- AlpineJS for client-side interactivity\n\n## Key Components\n- `app.py`: Main application entry point\n- `config.py`: Configuration settings including port (3149)\n- `app/models/`: Database models for Project, Sprint, Task, Issue\n- `app/routes/`: API endpoints and view controllers\n- `app/templates/`: Jinja2 templates with Tailwind CSS\n- `mcp/`: Model Context Protocol server for AI assistant integration'
            )
            db.session.add(project)
            db.session.commit()
            
            # Create sample sprints
            sprint1 = Sprint(
                name='Sprint 1: Initial Setup',
                description='Setting up the basic project structure and dependencies',
                status='Completed',
                project_id=project.id
            )
            
            sprint2 = Sprint(
                name='Sprint 2: Core Features',
                description='Implementing the core features of the application',
                status='Completed',
                project_id=project.id
            )
            
            sprint3 = Sprint(
                name='Sprint 3: UI Improvements',
                description='Enhancing the user interface with Tailwind and DaisyUI',
                status='Active',
                project_id=project.id
            )
            
            sprint4 = Sprint(
                name='Sprint 4: MCP Integration',
                description='Adding Model Context Protocol support for AI assistants',
                status='Planned',
                project_id=project.id
            )
            
            db.session.add_all([sprint1, sprint2, sprint3, sprint4])
            db.session.commit()
            
            # Create sample tasks for Sprint 1
            task1 = Task(
                details='Set up Flask project structure',
                completed=True,
                sprint_id=sprint1.id,
                starred=True
            )
            
            task2 = Task(
                details='Configure SQLAlchemy and create database models',
                completed=True,
                sprint_id=sprint1.id
            )
            
            task3 = Task(
                details='Set up basic routing and views',
                completed=True,
                sprint_id=sprint1.id
            )
            
            # Create sample tasks for Sprint 2
            task4 = Task(
                details='Implement project creation and management',
                completed=True,
                sprint_id=sprint2.id,
                starred=True
            )
            
            task5 = Task(
                details='Add sprint functionality',
                completed=True,
                sprint_id=sprint2.id
            )
            
            task6 = Task(
                details='Create task and issue tracking',
                completed=True,
                sprint_id=sprint2.id
            )
            
            # Create sample tasks for Sprint 3
            task7 = Task(
                details='Integrate Tailwind CSS and DaisyUI',
                completed=True,
                sprint_id=sprint3.id
            )
            
            task8 = Task(
                details='Implement responsive design for mobile',
                completed=False,
                sprint_id=sprint3.id,
                starred=True
            )
            
            task9 = Task(
                details='Add dark mode support',
                completed=False,
                sprint_id=sprint3.id
            )
            
            # Create sample tasks for Sprint 4
            task10 = Task(
                details='Set up MCP server structure',
                completed=False,
                sprint_id=sprint4.id
            )
            
            task11 = Task(
                details='Implement MCP tools for project management',
                completed=False,
                sprint_id=sprint4.id
            )
            
            # Create sample issues
            issue1 = Issue(
                details='Modal dialogs not working correctly on mobile devices',
                completed=False,
                sprint_id=sprint3.id,
                starred=True
            )
            
            issue2 = Issue(
                details='Task completion status not updating in real-time',
                completed=True,
                sprint_id=sprint2.id
            )
            
            issue3 = Issue(
                details='Need to improve error handling for API requests',
                completed=False,
                sprint_id=sprint4.id
            )
            
            db.session.add_all([task1, task2, task3, task4, task5, task6, task7, task8, task9, task10, task11, issue1, issue2, issue3])
            db.session.commit()
            
            print('Sample data created!')
        else:
            print('Sample data already exists, skipping creation.')
            
        print('Database initialization complete!')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Initialize the database and add sample data.')
    parser.add_argument('--reset', action='store_true', help='Reset the database (WARNING: This will delete all data!)')
    args = parser.parse_args()
    
    init_db(reset=args.reset)
