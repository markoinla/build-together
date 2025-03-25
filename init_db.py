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
        if Project.query.filter_by(name='Sample AI Project').first() is None:
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
            
            # Create sample tasks for Sprint 1
            task1 = Task(
                details='Research existing AI models',
                completed=True,
                sprint_id=sprint1.id
            )
            
            task2 = Task(
                details='Define project scope and requirements',
                completed=True,
                sprint_id=sprint1.id
            )
            
            # Create sample tasks for Sprint 2
            task3 = Task(
                details='Implement core AI algorithms',
                completed=False,
                sprint_id=sprint2.id
            )
            
            task4 = Task(
                details='Develop data preprocessing pipeline',
                completed=True,
                sprint_id=sprint2.id
            )
            
            # Create sample issues
            issue1 = Issue(
                details='Model accuracy is below 90%',
                completed=False,
                sprint_id=sprint2.id
            )
            
            db.session.add_all([task1, task2, task3, task4, issue1])
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
