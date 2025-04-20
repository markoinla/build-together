from flask import Blueprint, request, jsonify
from app import db
from app.models import Task, Sprint
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import Schema, fields, validate, ValidationError

# Create blueprint for task routes
task_bp = Blueprint('task', __name__, url_prefix='/api/tasks')

# Marshmallow schema for task validation
class TaskSchema(Schema):
    """
    Schema for validating task data using Marshmallow
    
    This defines the expected structure and validation rules for task data
    """
    details = fields.String(required=True)
    completed = fields.Boolean()
    sprint_id = fields.Integer(required=True)

# Marshmallow schema for task updates
class UpdateTaskSchema(Schema):
    """
    Schema for validating task updates using Marshmallow
    
    Similar to TaskSchema but does not require fields for updates
    """
    details = fields.String(required=False)
    completed = fields.Boolean(required=False)
    sprint_id = fields.Integer(required=False)

# Create schema instances
task_schema = TaskSchema()
update_task_schema = UpdateTaskSchema()

# Routes for tasks
@task_bp.route('', methods=['GET'])
def get_tasks():
    """
    API endpoint to get all tasks
    
    Optional query parameter:
        sprint_id: Filter tasks by sprint ID
    
    Returns:
        JSON response with array of all tasks
    """
    try:
        # Check if sprint_id query parameter is provided
        sprint_id = request.args.get('sprint_id', type=int)
        
        if sprint_id:
            # Get tasks for specific sprint
            tasks = Task.query.filter_by(sprint_id=sprint_id).all()
        else:
            # Get all tasks
            tasks = Task.query.all()
            
        return jsonify({
            'status': 'success',
            'data': [task.to_dict() for task in tasks]
        }), 200
    except SQLAlchemyError as e:
        return jsonify({
            'status': 'error',
            'message': 'Database error',
            'error': str(e)
        }), 500

@task_bp.route('/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """
    API endpoint to get a specific task by ID
    
    Args:
        task_id: ID of the task to retrieve
        
    Returns:
        JSON response with task data or error message
    """
    try:
        task = Task.query.get(task_id)
        
        if not task:
            return jsonify({
                'status': 'error',
                'message': f'Task with ID {task_id} not found'
            }), 404
            
        return jsonify({
            'status': 'success',
            'data': task.to_dict()
        }), 200
    except SQLAlchemyError as e:
        return jsonify({
            'status': 'error',
            'message': 'Database error',
            'error': str(e)
        }), 500

@task_bp.route('', methods=['POST'])
def create_task():
    """
    API endpoint to create a new task
    
    Request body should contain JSON with task data
    
    Returns:
        JSON response with created task or validation errors
    """
    try:
        # Get JSON data from request
        json_data = request.get_json()
        
        if not json_data:
            return jsonify({
                'status': 'error',
                'message': 'No input data provided'
            }), 400
            
        # Validate data
        errors = task_schema.validate(json_data)
        if errors:
            return jsonify({
                'status': 'error',
                'message': 'Validation error',
                'errors': errors
            }), 400
            
        # Verify sprint exists
        sprint = Sprint.query.get(json_data['sprint_id'])
        if not sprint:
            return jsonify({
                'status': 'error',
                'message': f'Sprint with ID {json_data["sprint_id"]} not found'
            }), 404
            
        # Create new task
        task = Task(
            details=json_data['details'],
            completed=json_data.get('completed', False),
            sprint_id=json_data['sprint_id']
        )
        
        # Add to database
        db.session.add(task)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Task created successfully',
            'data': task.to_dict()
        }), 201
    
    except ValidationError as e:
        return jsonify({
            'status': 'error',
            'message': 'Validation error',
            'errors': e.messages
        }), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Database error',
            'error': str(e)
        }), 500

@task_bp.route('/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """
    API endpoint to update an existing task
    
    Args:
        task_id: ID of the task to update
        
    Returns:
        JSON response with updated task or error message
    """
    try:
        # Get task
        task = Task.query.get(task_id)
        
        if not task:
            return jsonify({
                'status': 'error',
                'message': f'Task with ID {task_id} not found'
            }), 404
            
        # Get JSON data from request
        json_data = request.get_json()
        
        if not json_data:
            return jsonify({
                'status': 'error',
                'message': 'No input data provided'
            }), 400
            
        # Validate data using update schema that doesn't require all fields
        errors = update_task_schema.validate(json_data)
        if errors:
            return jsonify({
                'status': 'error',
                'message': 'Validation error',
                'errors': errors
            }), 400
            
        # If sprint_id is changing, verify new sprint exists
        if 'sprint_id' in json_data and json_data['sprint_id'] != task.sprint_id:
            sprint = Sprint.query.get(json_data['sprint_id'])
            if not sprint:
                return jsonify({
                    'status': 'error',
                    'message': f'Sprint with ID {json_data["sprint_id"]} not found'
                }), 404
                
        # Update task
        task.details = json_data.get('details', task.details)
        if 'completed' in json_data:
            task.completed = json_data['completed']
        task.sprint_id = json_data.get('sprint_id', task.sprint_id)
        
        # Save changes
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Task updated successfully',
            'data': task.to_dict()
        }), 200
        
    except ValidationError as e:
        return jsonify({
            'status': 'error',
            'message': 'Validation error',
            'errors': e.messages
        }), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Database error',
            'error': str(e)
        }), 500

@task_bp.route('/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """
    API endpoint to delete a task
    
    Args:
        task_id: ID of the task to delete
        
    Returns:
        JSON response with success message or error
    """
    try:
        # Get task
        task = Task.query.get(task_id)
        
        if not task:
            return jsonify({
                'status': 'error',
                'message': f'Task with ID {task_id} not found'
            }), 404
            
        # Delete task
        db.session.delete(task)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Task deleted successfully'
        }), 200
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Database error',
            'error': str(e)
        }), 500
