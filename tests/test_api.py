"""
Tests for the BTG API endpoints.

This file contains tests for the RESTful API endpoints of the BTG application.
It tests the CRUD operations for Projects, Sprints, Tasks, and Issues.
"""
import os
import sys
import pytest
import json
import tempfile

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Project, Sprint, Task, Issue
from config import Config

# Test configuration
class TestConfig(Config):
    """Test configuration that uses a temporary SQLite database"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


@pytest.fixture
def client():
    """
    Test client fixture
    
    Creates a test client with a temporary database for testing
    """
    # Create the Flask app with test configuration
    app = create_app(TestConfig)
    
    # Create a test client
    with app.test_client() as client:
        # Create application context
        with app.app_context():
            # Create the database and tables
            db.create_all()
            
            # Add some test data
            create_test_data()
            
            yield client
            
            # Clean up
            db.session.remove()
            db.drop_all()


def create_test_data():
    """
    Create test data for the test database
    
    This creates a test project, sprint, task, and issue
    """
    # Create a test project
    project = Project(
        name='Test Project',
        description='Test Description',
        requirements='Test Requirements'
    )
    db.session.add(project)
    db.session.commit()
    
    # Create a test sprint
    sprint = Sprint(
        name='Test Sprint',
        description='Test Description',
        status='Planned',
        project_id=project.id
    )
    db.session.add(sprint)
    db.session.commit()
    
    # Create a test task
    task = Task(
        details='Test Task',
        completed=False,
        sprint_id=sprint.id
    )
    db.session.add(task)
    
    # Create a test issue
    issue = Issue(
        details='Test Issue',
        completed=False,
        sprint_id=sprint.id
    )
    db.session.add(issue)
    db.session.commit()


# Project API Tests
def test_get_projects(client):
    """Test getting all projects"""
    response = client.get('/api/projects')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert len(data['data']) == 1
    assert data['data'][0]['name'] == 'Test Project'


def test_get_project(client):
    """Test getting a specific project"""
    # Get the test project
    project = Project.query.filter_by(name='Test Project').first()
    
    # Test getting the project
    response = client.get(f'/api/projects/{project.id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['data']['name'] == 'Test Project'
    assert data['data']['description'] == 'Test Description'
    assert data['data']['requirements'] == 'Test Requirements'
    assert len(data['data']['sprints']) == 1


def test_create_project(client):
    """Test creating a new project"""
    # Create a new project
    response = client.post('/api/projects', json={
        'name': 'New Project',
        'description': 'New Description',
        'requirements': 'New Requirements'
    })
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['data']['name'] == 'New Project'
    
    # Verify the project was created
    project = Project.query.filter_by(name='New Project').first()
    assert project is not None
    assert project.description == 'New Description'
    assert project.requirements == 'New Requirements'


def test_update_project(client):
    """Test updating a project"""
    # Get the test project
    project = Project.query.filter_by(name='Test Project').first()
    
    # Update the project
    response = client.put(f'/api/projects/{project.id}', json={
        'name': 'Updated Project',
        'description': 'Updated Description',
        'requirements': 'Updated Requirements'
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['data']['name'] == 'Updated Project'
    
    # Verify the project was updated
    updated_project = Project.query.get(project.id)
    assert updated_project.name == 'Updated Project'
    assert updated_project.description == 'Updated Description'
    assert updated_project.requirements == 'Updated Requirements'


def test_delete_project(client):
    """Test deleting a project"""
    # Get the test project
    project = Project.query.filter_by(name='Test Project').first()
    
    # Delete the project
    response = client.delete(f'/api/projects/{project.id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    
    # Verify the project was deleted
    deleted_project = Project.query.get(project.id)
    assert deleted_project is None


# Sprint API Tests
def test_get_sprints(client):
    """Test getting all sprints"""
    response = client.get('/api/sprints')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert len(data['data']) == 1
    assert data['data'][0]['name'] == 'Test Sprint'


def test_get_sprint(client):
    """Test getting a specific sprint"""
    # Get the test sprint
    sprint = Sprint.query.filter_by(name='Test Sprint').first()
    
    # Test getting the sprint
    response = client.get(f'/api/sprints/{sprint.id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['data']['name'] == 'Test Sprint'
    assert data['data']['description'] == 'Test Description'
    assert data['data']['status'] == 'Planned'
    assert len(data['data']['tasks']) == 1
    assert len(data['data']['issues']) == 1


def test_create_sprint(client):
    """Test creating a new sprint"""
    # Get the test project
    project = Project.query.filter_by(name='Test Project').first()
    
    # Create a new sprint
    response = client.post('/api/sprints', json={
        'name': 'New Sprint',
        'description': 'New Description',
        'status': 'Active',
        'project_id': project.id
    })
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['data']['name'] == 'New Sprint'
    
    # Verify the sprint was created
    sprint = Sprint.query.filter_by(name='New Sprint').first()
    assert sprint is not None
    assert sprint.description == 'New Description'
    assert sprint.status == 'Active'
    assert sprint.project_id == project.id


def test_update_sprint(client):
    """Test updating a sprint"""
    # Get the test sprint
    sprint = Sprint.query.filter_by(name='Test Sprint').first()
    # Get the test project
    project = Project.query.filter_by(name='Test Project').first()
    
    # Update the sprint - include project_id which is required by the schema
    response = client.put(f'/api/sprints/{sprint.id}', json={
        'name': 'Updated Sprint',
        'description': 'Updated Description',
        'status': 'Completed',
        'project_id': project.id  # Include the project_id to satisfy schema validation
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['data']['name'] == 'Updated Sprint'
    
    # Verify the sprint was updated
    updated_sprint = Sprint.query.get(sprint.id)
    assert updated_sprint.name == 'Updated Sprint'
    assert updated_sprint.description == 'Updated Description'
    assert updated_sprint.status == 'Completed'


def test_delete_sprint(client):
    """Test deleting a sprint"""
    # Get the test sprint
    sprint = Sprint.query.filter_by(name='Test Sprint').first()
    
    # Delete the sprint
    response = client.delete(f'/api/sprints/{sprint.id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    
    # Verify the sprint was deleted
    deleted_sprint = Sprint.query.get(sprint.id)
    assert deleted_sprint is None


# Task API Tests
def test_get_tasks(client):
    """Test getting all tasks"""
    response = client.get('/api/tasks')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert len(data['data']) == 1
    assert data['data'][0]['details'] == 'Test Task'


def test_get_task(client):
    """Test getting a specific task"""
    # Get the test task
    task = Task.query.filter_by(details='Test Task').first()
    
    # Test getting the task
    response = client.get(f'/api/tasks/{task.id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['data']['details'] == 'Test Task'
    assert data['data']['completed'] == False


def test_create_task(client):
    """Test creating a new task"""
    # Get the test sprint
    sprint = Sprint.query.filter_by(name='Test Sprint').first()
    
    # Create a new task
    response = client.post('/api/tasks', json={
        'details': 'New Task',
        'completed': True,
        'sprint_id': sprint.id
    })
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['data']['details'] == 'New Task'
    
    # Verify the task was created
    task = Task.query.filter_by(details='New Task').first()
    assert task is not None
    assert task.completed == True
    assert task.sprint_id == sprint.id


def test_update_task(client):
    """Test updating a task"""
    # Get the test task
    task = Task.query.filter_by(details='Test Task').first()
    # Get the test sprint
    sprint = Sprint.query.filter_by(name='Test Sprint').first()
    
    # Update the task - include sprint_id which is required by the schema
    response = client.put(f'/api/tasks/{task.id}', json={
        'details': 'Updated Task',
        'completed': True,
        'sprint_id': sprint.id  # Include the sprint_id to satisfy schema validation
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['data']['details'] == 'Updated Task'
    
    # Verify the task was updated
    updated_task = Task.query.get(task.id)
    assert updated_task.details == 'Updated Task'
    assert updated_task.completed == True


def test_delete_task(client):
    """Test deleting a task"""
    # Get the test task
    task = Task.query.filter_by(details='Test Task').first()
    
    # Delete the task
    response = client.delete(f'/api/tasks/{task.id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    
    # Verify the task was deleted
    deleted_task = Task.query.get(task.id)
    assert deleted_task is None


# Issue API Tests
def test_get_issues(client):
    """Test getting all issues"""
    response = client.get('/api/issues')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert len(data['data']) == 1
    assert data['data'][0]['details'] == 'Test Issue'


def test_get_issue(client):
    """Test getting a specific issue"""
    # Get the test issue
    issue = Issue.query.filter_by(details='Test Issue').first()
    
    # Test getting the issue
    response = client.get(f'/api/issues/{issue.id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['data']['details'] == 'Test Issue'
    assert data['data']['completed'] == False


def test_create_issue(client):
    """Test creating a new issue"""
    # Get the test sprint
    sprint = Sprint.query.filter_by(name='Test Sprint').first()
    
    # Create a new issue
    response = client.post('/api/issues', json={
        'details': 'New Issue',
        'completed': True,
        'sprint_id': sprint.id
    })
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['data']['details'] == 'New Issue'
    
    # Verify the issue was created
    issue = Issue.query.filter_by(details='New Issue').first()
    assert issue is not None
    assert issue.completed == True
    assert issue.sprint_id == sprint.id


def test_update_issue(client):
    """Test updating an issue"""
    # Get the test issue
    issue = Issue.query.filter_by(details='Test Issue').first()
    # Get the test sprint
    sprint = Sprint.query.filter_by(name='Test Sprint').first()
    
    # Update the issue - include sprint_id which is required by the schema
    response = client.put(f'/api/issues/{issue.id}', json={
        'details': 'Updated Issue',
        'completed': True,
        'sprint_id': sprint.id  # Include the sprint_id to satisfy schema validation
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['data']['details'] == 'Updated Issue'
    
    # Verify the issue was updated
    updated_issue = Issue.query.get(issue.id)
    assert updated_issue.details == 'Updated Issue'
    assert updated_issue.completed == True


def test_delete_issue(client):
    """Test deleting an issue"""
    # Get the test issue
    issue = Issue.query.filter_by(details='Test Issue').first()
    
    # Delete the issue
    response = client.delete(f'/api/issues/{issue.id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    
    # Verify the issue was deleted
    deleted_issue = Issue.query.get(issue.id)
    assert deleted_issue is None
