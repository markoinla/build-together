from flask import Blueprint, request, jsonify
from app import db
from app.models import Sprint, Project
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import Schema, fields, validate, ValidationError

# Create blueprint for sprint routes
sprint_bp = Blueprint('sprint', __name__, url_prefix='/api/sprints')

# Marshmallow schema for sprint validation
class SprintSchema(Schema):
    """
    Schema for validating sprint data using Marshmallow
    
    This defines the expected structure and validation rules for sprint data
    """
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    description = fields.String(allow_none=True)
    status = fields.String(validate=validate.OneOf(['Planned', 'Active', 'Completed']))
    project_id = fields.Integer(required=True)
    
# Marshmallow schema for sprint updates
class UpdateSprintSchema(Schema):
    """
    Schema for validating sprint updates using Marshmallow
    
    Similar to SprintSchema but does not require fields for updates
    """
    name = fields.String(required=False, validate=validate.Length(min=1, max=100))
    description = fields.String(allow_none=True)
    status = fields.String(validate=validate.OneOf(['Planned', 'Active', 'Completed']))
    project_id = fields.Integer(required=False)

# Create schema instances
sprint_schema = SprintSchema()
update_sprint_schema = UpdateSprintSchema()

# Routes for sprints
@sprint_bp.route('', methods=['GET'])
def get_sprints():
    """
    API endpoint to get all sprints
    
    Optional query parameter:
        project_id: Filter sprints by project ID
    
    Returns:
        JSON response with array of all sprints
    """
    try:
        # Check if project_id query parameter is provided
        project_id = request.args.get('project_id', type=int)
        
        if project_id:
            # Get sprints for specific project
            sprints = Sprint.query.filter_by(project_id=project_id).all()
        else:
            # Get all sprints
            sprints = Sprint.query.all()
            
        return jsonify({
            'status': 'success',
            'data': [sprint.to_dict_simple() for sprint in sprints]
        }), 200
    except SQLAlchemyError as e:
        return jsonify({
            'status': 'error',
            'message': 'Database error',
            'error': str(e)
        }), 500

@sprint_bp.route('/<int:sprint_id>', methods=['GET'])
def get_sprint(sprint_id):
    """
    API endpoint to get a specific sprint by ID
    
    Args:
        sprint_id: ID of the sprint to retrieve
        
    Returns:
        JSON response with sprint data or error message
    """
    try:
        sprint = Sprint.query.get(sprint_id)
        
        if not sprint:
            return jsonify({
                'status': 'error',
                'message': f'Sprint with ID {sprint_id} not found'
            }), 404
            
        return jsonify({
            'status': 'success',
            'data': sprint.to_dict()
        }), 200
    except SQLAlchemyError as e:
        return jsonify({
            'status': 'error',
            'message': 'Database error',
            'error': str(e)
        }), 500

@sprint_bp.route('', methods=['POST'])
def create_sprint():
    """
    API endpoint to create a new sprint
    
    Request body should contain JSON with sprint data
    
    Returns:
        JSON response with created sprint or validation errors
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
        errors = sprint_schema.validate(json_data)
        if errors:
            return jsonify({
                'status': 'error',
                'message': 'Validation error',
                'errors': errors
            }), 400
            
        # Verify project exists
        project = Project.query.get(json_data['project_id'])
        if not project:
            return jsonify({
                'status': 'error',
                'message': f'Project with ID {json_data["project_id"]} not found'
            }), 404
            
        # Create new sprint
        sprint = Sprint(
            name=json_data['name'],
            description=json_data.get('description'),
            status=json_data.get('status', 'Planned'),
            project_id=json_data['project_id']
        )
        
        # Add to database
        db.session.add(sprint)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Sprint created successfully',
            'data': sprint.to_dict()
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

@sprint_bp.route('/<int:sprint_id>', methods=['PUT'])
def update_sprint(sprint_id):
    """
    API endpoint to update an existing sprint
    
    Args:
        sprint_id: ID of the sprint to update
        
    Returns:
        JSON response with updated sprint or error message
    """
    try:
        # Get sprint
        sprint = Sprint.query.get(sprint_id)
        
        if not sprint:
            return jsonify({
                'status': 'error',
                'message': f'Sprint with ID {sprint_id} not found'
            }), 404
            
        # Get JSON data from request
        json_data = request.get_json()
        
        if not json_data:
            return jsonify({
                'status': 'error',
                'message': 'No input data provided'
            }), 400
            
        # Validate data using update schema that doesn't require all fields
        errors = update_sprint_schema.validate(json_data)
        if errors:
            return jsonify({
                'status': 'error',
                'message': 'Validation error',
                'errors': errors
            }), 400
            
        # If project_id is changing, verify new project exists
        if 'project_id' in json_data and json_data['project_id'] != sprint.project_id:
            project = Project.query.get(json_data['project_id'])
            if not project:
                return jsonify({
                    'status': 'error',
                    'message': f'Project with ID {json_data["project_id"]} not found'
                }), 404
                
        # Update sprint
        sprint.name = json_data.get('name', sprint.name)
        sprint.description = json_data.get('description', sprint.description)
        sprint.status = json_data.get('status', sprint.status)
        sprint.project_id = json_data.get('project_id', sprint.project_id)
        
        # Save changes
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Sprint updated successfully',
            'data': sprint.to_dict()
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

@sprint_bp.route('/<int:sprint_id>', methods=['DELETE'])
def delete_sprint(sprint_id):
    """
    API endpoint to delete a sprint
    
    Args:
        sprint_id: ID of the sprint to delete
        
    Returns:
        JSON response with success message or error
    """
    try:
        # Get sprint
        sprint = Sprint.query.get(sprint_id)
        
        if not sprint:
            return jsonify({
                'status': 'error',
                'message': f'Sprint with ID {sprint_id} not found'
            }), 404
            
        # Delete sprint
        db.session.delete(sprint)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Sprint deleted successfully'
        }), 200
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Database error',
            'error': str(e)
        }), 500
