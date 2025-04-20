from flask import Blueprint, request, jsonify
from app import db
from app.models import Issue, Sprint
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import Schema, fields, validate, ValidationError

# Create blueprint for issue routes
issue_bp = Blueprint('issue', __name__, url_prefix='/api/issues')

# Marshmallow schema for issue validation
class IssueSchema(Schema):
    """
    Schema for validating issue data using Marshmallow
    
    This defines the expected structure and validation rules for issue data
    """
    details = fields.String(required=True)
    completed = fields.Boolean()
    sprint_id = fields.Integer(required=True)

# Marshmallow schema for issue updates
class UpdateIssueSchema(Schema):
    """
    Schema for validating issue updates using Marshmallow
    
    Similar to IssueSchema but does not require fields for updates
    """
    details = fields.String(required=False)
    completed = fields.Boolean(required=False)
    sprint_id = fields.Integer(required=False)

# Create schema instances
issue_schema = IssueSchema()
update_issue_schema = UpdateIssueSchema()

# Routes for issues
@issue_bp.route('', methods=['GET'])
def get_issues():
    """
    API endpoint to get all issues
    
    Optional query parameter:
        sprint_id: Filter issues by sprint ID
    
    Returns:
        JSON response with array of all issues
    """
    try:
        # Check if sprint_id query parameter is provided
        sprint_id = request.args.get('sprint_id', type=int)
        
        if sprint_id:
            # Get issues for specific sprint
            issues = Issue.query.filter_by(sprint_id=sprint_id).all()
        else:
            # Get all issues
            issues = Issue.query.all()
            
        return jsonify({
            'status': 'success',
            'data': [issue.to_dict() for issue in issues]
        }), 200
    except SQLAlchemyError as e:
        return jsonify({
            'status': 'error',
            'message': 'Database error',
            'error': str(e)
        }), 500

@issue_bp.route('/<int:issue_id>', methods=['GET'])
def get_issue(issue_id):
    """
    API endpoint to get a specific issue by ID
    
    Args:
        issue_id: ID of the issue to retrieve
        
    Returns:
        JSON response with issue data or error message
    """
    try:
        issue = Issue.query.get(issue_id)
        
        if not issue:
            return jsonify({
                'status': 'error',
                'message': f'Issue with ID {issue_id} not found'
            }), 404
            
        return jsonify({
            'status': 'success',
            'data': issue.to_dict()
        }), 200
    except SQLAlchemyError as e:
        return jsonify({
            'status': 'error',
            'message': 'Database error',
            'error': str(e)
        }), 500

@issue_bp.route('', methods=['POST'])
def create_issue():
    """
    API endpoint to create a new issue
    
    Request body should contain JSON with issue data
    
    Returns:
        JSON response with created issue or validation errors
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
        errors = issue_schema.validate(json_data)
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
            
        # Create new issue
        issue = Issue(
            details=json_data['details'],
            completed=json_data.get('completed', False),
            sprint_id=json_data['sprint_id']
        )
        
        # Add to database
        db.session.add(issue)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Issue created successfully',
            'data': issue.to_dict()
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

@issue_bp.route('/<int:issue_id>', methods=['PUT'])
def update_issue(issue_id):
    """
    API endpoint to update an existing issue
    
    Args:
        issue_id: ID of the issue to update
        
    Returns:
        JSON response with updated issue or error message
    """
    try:
        # Get issue
        issue = Issue.query.get(issue_id)
        
        if not issue:
            return jsonify({
                'status': 'error',
                'message': f'Issue with ID {issue_id} not found'
            }), 404
            
        # Get JSON data from request
        json_data = request.get_json()
        
        if not json_data:
            return jsonify({
                'status': 'error',
                'message': 'No input data provided'
            }), 400
            
        # Validate data using update schema that doesn't require all fields
        errors = update_issue_schema.validate(json_data)
        if errors:
            return jsonify({
                'status': 'error',
                'message': 'Validation error',
                'errors': errors
            }), 400
            
        # If sprint_id is changing, verify new sprint exists
        if 'sprint_id' in json_data and json_data['sprint_id'] != issue.sprint_id:
            sprint = Sprint.query.get(json_data['sprint_id'])
            if not sprint:
                return jsonify({
                    'status': 'error',
                    'message': f'Sprint with ID {json_data["sprint_id"]} not found'
                }), 404
                
        # Update issue
        issue.details = json_data.get('details', issue.details)
        if 'completed' in json_data:
            issue.completed = json_data['completed']
        issue.sprint_id = json_data.get('sprint_id', issue.sprint_id)
        
        # Save changes
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Issue updated successfully',
            'data': issue.to_dict()
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

@issue_bp.route('/<int:issue_id>', methods=['DELETE'])
def delete_issue(issue_id):
    """
    API endpoint to delete an issue
    
    Args:
        issue_id: ID of the issue to delete
        
    Returns:
        JSON response with success message or error
    """
    try:
        # Get issue
        issue = Issue.query.get(issue_id)
        
        if not issue:
            return jsonify({
                'status': 'error',
                'message': f'Issue with ID {issue_id} not found'
            }), 404
            
        # Delete issue
        db.session.delete(issue)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Issue deleted successfully'
        }), 200
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            'status': 'error',
            'message': 'Database error',
            'error': str(e)
        }), 500
