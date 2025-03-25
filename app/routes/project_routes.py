from flask import Blueprint, request, jsonify, render_template
from app import db
from app.models import Project
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import Schema, fields, validate, ValidationError

# Create blueprint for project routes
project_bp = Blueprint('project', __name__, url_prefix='/api/projects')

# Marshmallow schema for project validation
class ProjectSchema(Schema):
    """
    Schema for validating project data using Marshmallow
    
    This defines the expected structure and validation rules for project data
    """
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    description = fields.String(allow_none=True)
    requirements = fields.String(allow_none=True)

# Schema for updating projects - name not required
class UpdateProjectSchema(Schema):
    """
    Schema for validating project updates using Marshmallow
    
    Similar to ProjectSchema but does not require name field for updates
    """
    name = fields.String(required=False, validate=validate.Length(min=1, max=100))
    description = fields.String(allow_none=True)
    requirements = fields.String(allow_none=True)
    implementation_details = fields.String(allow_none=True)

# Create schema instances
project_schema = ProjectSchema()
update_project_schema = UpdateProjectSchema()

# Routes for projects
@project_bp.route('', methods=['GET'])
def get_projects():
    """
    API endpoint to get all projects
    
    Returns:
        JSON response with array of all projects
    """
    try:
        projects = Project.query.all()
        return jsonify({
            'status': 'success',
            'data': [project.to_dict_simple() for project in projects]
        }), 200
    except SQLAlchemyError as e:
        return jsonify({
            'status': 'error',
            'message': 'Database error',
            'error': str(e)
        }), 500

@project_bp.route('/<int:project_id>', methods=['GET'])
def get_project(project_id):
    """
    API endpoint to get a specific project by ID
    
    Args:
        project_id: ID of the project to retrieve
        
    Returns:
        JSON response with project data or error message
    """
    try:
        project = Project.query.get(project_id)
        
        if not project:
            return jsonify({
                'status': 'error',
                'message': f'Project with ID {project_id} not found'
            }), 404
            
        return jsonify({
            'status': 'success',
            'data': project.to_dict()
        }), 200
    except SQLAlchemyError as e:
        return jsonify({
            'status': 'error',
            'message': 'Database error',
            'error': str(e)
        }), 500

@project_bp.route('', methods=['POST'])
def create_project():
    """
    API endpoint to create a new project
    
    Request body should contain JSON with project data
    
    Returns:
        JSON response with created project or validation errors
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
        errors = project_schema.validate(json_data)
        if errors:
            return jsonify({
                'status': 'error',
                'message': 'Validation error',
                'errors': errors
            }), 400
            
        # Create new project
        project = Project(
            name=json_data['name'],
            description=json_data.get('description'),
            requirements=json_data.get('requirements')
        )
        
        # Add to database
        db.session.add(project)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Project created successfully',
            'data': project.to_dict()
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

@project_bp.route('/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    """
    API endpoint to update an existing project
    
    Args:
        project_id: ID of the project to update
        
    Returns:
        JSON response with updated project or error message
    """
    try:
        # Get project
        project = Project.query.get(project_id)
        
        if not project:
            return jsonify({
                'status': 'error',
                'message': f'Project with ID {project_id} not found'
            }), 404
            
        # Get JSON data from request
        json_data = request.get_json()
        
        if not json_data:
            return jsonify({
                'status': 'error',
                'message': 'No input data provided'
            }), 400
            
        # Validate data
        errors = update_project_schema.validate(json_data)
        if errors:
            return jsonify({
                'status': 'error',
                'message': 'Validation error',
                'errors': errors
            }), 400
            
        # Update project
        project.name = json_data.get('name', project.name)
        project.description = json_data.get('description', project.description)
        project.requirements = json_data.get('requirements', project.requirements)
        project.implementation_details = json_data.get('implementation_details')
        
        # Save changes
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Project updated successfully',
            'data': project.to_dict()
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

@project_bp.route('/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    """
    API endpoint to delete a project
    
    Args:
        project_id: ID of the project to delete
        
    Returns:
        JSON response with success message or error
    """
    try:
        # Get project
        project = Project.query.get(project_id)
        
        if not project:
            return jsonify({
                'status': 'error',
                'message': f'Project with ID {project_id} not found'
            }), 404
            
        # Delete project
        db.session.delete(project)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Project deleted successfully'
        }), 200
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Database error',
            'error': str(e)
        }), 500
