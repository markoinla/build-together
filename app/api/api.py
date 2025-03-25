"""
MCP API Endpoints

This module provides API endpoints for the standalone MCP server to interact with
the Build Together (BTG) application. These endpoints implement the necessary functionality
for the MCP tools without duplicating the MCP server implementation.
"""

from flask import Blueprint, jsonify, request
from app.models.project import Project
from app.models.sprint import Sprint
from app.models.task import Task
from app.models.issue import Issue
from app import db

# Create a blueprint for MCP API endpoints
mcp_api_bp = Blueprint('mcp_api', __name__, url_prefix='/mcp')

# Define an empty tools dictionary that will be populated after all functions are defined
TOOLS = {}

# Helper functions to replace the ones from tool_definitions
def get_tool_definition(tool_name):
    """Get tool definition by name"""
    return TOOLS.get(tool_name)

def get_tool_parameters(tool_name):
    """Get parameters for a tool (placeholder for now)"""
    return {}

@mcp_api_bp.route('/', methods=['GET'])
def mcp_root():
    """Root endpoint for the MCP server"""
    return jsonify({"message": "Build Together (BTG) MCP Server is running"})

@mcp_api_bp.route('/ping', methods=['GET'])
def ping():
    """Simple ping endpoint to check connection and warm up connection"""
    return jsonify({"status": "ok", "message": "pong"})

@mcp_api_bp.route('/tools', methods=['GET'])
def get_tools():
    """Return the list of available tools"""
    # Return tool definitions with descriptions for the MCP inspector
    tool_definitions = []
    for name, func in TOOLS.items():
        description = func.__doc__ or f"Execute the {name} tool"
        tool_definitions.append({
            "name": name,
            "description": description.strip()
        })
    return jsonify(tool_definitions)

@mcp_api_bp.route('/execute', methods=['POST'])
def execute_tool():
    """Execute a tool based on the request"""
    data = request.get_json()
    tool_name = data.get("name")
    parameters = data.get("parameters", {}) or data.get("arguments", {})
    
    # Log the received parameters for debugging
    print(f"MCP execute tool: {tool_name} with parameters: {parameters}")
    
    # Find the tool implementation
    tool_impl = TOOLS.get(tool_name)
    if not tool_impl:
        return jsonify({"error": f"Tool '{tool_name}' not found"})
    
    # Handle parameter validation to ensure we only use parameters that match our data model
    if tool_name in ['create_task', 'update_task', 'create_issue', 'update_issue']:
        # If old parameter names are used, return an error with guidance
        if 'title' in parameters or 'description' in parameters:
            return jsonify({
                "error": f"Invalid parameters for tool '{tool_name}'. Use 'details' instead of 'title' or 'description' to match the data model."
            })
    
    # Execute the tool with the provided parameters
    try:
        # Ensure boolean parameters are properly handled
        for key, value in parameters.items():
            if isinstance(value, str) and value.lower() in ['true', 'false']:
                parameters[key] = value.lower() == 'true'
        
        result = tool_impl(**parameters)
        return jsonify({"result": result})
    except Exception as e:
        return jsonify({"error": str(e)})

# Tool implementations

def list_projects():
    """List all projects"""
    projects = Project.query.all()
    return [project.to_dict() for project in projects]

def get_project(project_id):
    """Get a project by ID"""
    project = Project.query.get(project_id)
    if not project:
        return {"error": f"Project with ID {project_id} not found"}
    return project.to_dict()

def create_project(name, description=""):
    """Create a new project"""
    project = Project(name=name, description=description)
    db.session.add(project)
    db.session.commit()
    return project.to_dict()

def update_project(project_id, name=None, description=None, requirements=None, implementation_details=None):
    """Update an existing project"""
    project = Project.query.get(project_id)
    if not project:
        return {"error": f"Project with ID {project_id} not found"}
    
    if name is not None:
        project.name = name
    if description is not None:
        project.description = description
    if requirements is not None:
        project.requirements = requirements
    if implementation_details is not None:
        project.implementation_details = implementation_details
    
    db.session.commit()
    return project.to_dict()

def delete_project(project_id):
    """Delete a project by ID"""
    project = Project.query.get(project_id)
    if not project:
        return {"error": f"Project with ID {project_id} not found"}
    
    db.session.delete(project)
    db.session.commit()
    return {"success": True, "message": f"Project with ID {project_id} deleted"}

def list_sprints(project_id=None):
    """List all sprints, optionally filtered by project ID"""
    if project_id:
        sprints = Sprint.query.filter_by(project_id=project_id).all()
    else:
        sprints = Sprint.query.all()
    return [sprint.to_dict() for sprint in sprints]

def get_sprint(sprint_id):
    """Get a sprint by ID"""
    sprint = Sprint.query.get(sprint_id)
    if not sprint:
        return {"error": f"Sprint with ID {sprint_id} not found"}
    return sprint.to_dict()

def create_sprint(name, project_id, description=None, status="Planned"):
    """Create a new sprint"""
    # Validate status if provided
    if status and status not in Sprint.VALID_STATUSES:
        return {"error": f"Invalid status: {status}. Must be one of {Sprint.VALID_STATUSES}"}
        
    sprint = Sprint(name=name, project_id=project_id)
    
    if description is not None:
        sprint.description = description
    if status is not None:
        sprint.status = status
        
    db.session.add(sprint)
    db.session.commit()
    return sprint.to_dict()

def update_sprint(sprint_id, name=None, project_id=None, description=None, status=None):
    """Update an existing sprint"""
    sprint = Sprint.query.get(sprint_id)
    if not sprint:
        return {"error": f"Sprint with ID {sprint_id} not found"}
    
    # Validate status if provided
    if status and status not in Sprint.VALID_STATUSES:
        return {"error": f"Invalid status: {status}. Must be one of {Sprint.VALID_STATUSES}"}
    
    if name is not None:
        sprint.name = name
    if project_id is not None:
        sprint.project_id = project_id
    if description is not None:
        sprint.description = description
    if status is not None:
        sprint.status = status
    
    db.session.commit()
    return sprint.to_dict()

def delete_sprint(sprint_id):
    """Delete a sprint by ID"""
    sprint = Sprint.query.get(sprint_id)
    if not sprint:
        return {"error": f"Sprint with ID {sprint_id} not found"}
    
    db.session.delete(sprint)
    db.session.commit()
    return {"success": True, "message": f"Sprint with ID {sprint_id} deleted"}

def list_tasks(sprint_id=None):
    """List all tasks, optionally filtered by sprint ID"""
    if sprint_id:
        tasks = Task.query.filter_by(sprint_id=sprint_id).all()
    else:
        tasks = Task.query.all()
    return [task.to_dict() for task in tasks]

def get_task(task_id):
    """Get a task by ID"""
    task = Task.query.get(task_id)
    if not task:
        return {"error": f"Task with ID {task_id} not found"}
    return task.to_dict()

def create_task(details, sprint_id, completed=False):
    """Create a new task"""
    task = Task(details=details, sprint_id=sprint_id, completed=completed)
    db.session.add(task)
    db.session.commit()
    return task.to_dict()

def update_task(task_id, details=None, sprint_id=None, completed=None):
    """Update an existing task"""
    task = Task.query.get(task_id)
    if not task:
        return {"error": f"Task with ID {task_id} not found"}
    
    if details is not None:
        task.details = details
    if sprint_id is not None:
        task.sprint_id = sprint_id
    if completed is not None:
        task.completed = completed
    
    db.session.commit()
    return task.to_dict()

def delete_task(task_id):
    """Delete a task by ID"""
    task = Task.query.get(task_id)
    if not task:
        return {"error": f"Task with ID {task_id} not found"}
    
    db.session.delete(task)
    db.session.commit()
    return {"success": True, "message": f"Task with ID {task_id} deleted"}

def list_issues(sprint_id=None):
    """List all issues, optionally filtered by sprint ID"""
    if sprint_id:
        issues = Issue.query.filter_by(sprint_id=sprint_id).all()
    else:
        issues = Issue.query.all()
    return [issue.to_dict() for issue in issues]

def get_issue(issue_id):
    """Get an issue by ID"""
    issue = Issue.query.get(issue_id)
    if not issue:
        return {"error": f"Issue with ID {issue_id} not found"}
    return issue.to_dict()

def create_issue(details, sprint_id, completed=False):
    """Create a new issue"""
    issue = Issue(details=details, sprint_id=sprint_id, completed=completed)
    db.session.add(issue)
    db.session.commit()
    return issue.to_dict()

def update_issue(issue_id, details=None, sprint_id=None, completed=None):
    """Update an existing issue"""
    issue = Issue.query.get(issue_id)
    if not issue:
        return {"error": f"Issue with ID {issue_id} not found"}
    
    if details is not None:
        issue.details = details
    if sprint_id is not None:
        issue.sprint_id = sprint_id
    if completed is not None:
        issue.completed = completed
    
    db.session.commit()
    return issue.to_dict()

def delete_issue(issue_id):
    """Delete an issue by ID"""
    issue = Issue.query.get(issue_id)
    if not issue:
        return {"error": f"Issue with ID {issue_id} not found"}
    
    db.session.delete(issue)
    db.session.commit()
    return {"success": True, "message": f"Issue with ID {issue_id} deleted"}

# Now populate the TOOLS dictionary with all the functions after they've been defined
TOOLS = {
    "list_projects": list_projects,
    "get_project": get_project,
    "create_project": create_project,
    "update_project": update_project,
    "delete_project": delete_project,
    "list_sprints": list_sprints,
    "get_sprint": get_sprint,
    "create_sprint": create_sprint,
    "update_sprint": update_sprint,
    "delete_sprint": delete_sprint,
    "list_tasks": list_tasks,
    "get_task": get_task,
    "create_task": create_task,
    "update_task": update_task,
    "delete_task": delete_task,
    "list_issues": list_issues,
    "get_issue": get_issue,
    "create_issue": create_issue,
    "update_issue": update_issue,
    "delete_issue": delete_issue
}
