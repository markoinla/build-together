#!/usr/bin/env python3
"""
Build Together MCP Server
Provides tools for retrieving project information and managing the Build Together app
"""

import logging
import sys
import requests
from typing import List, Dict, Any
import json
import argparse
from mcp.server.fastmcp import FastMCP

# Configure basic logging to see what's happening
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger("build-together-mcp")

# Parse command line arguments
parser = argparse.ArgumentParser(description="Build Together MCP Server")
parser.add_argument("--port", type=int, default=3149, help="Port where the Build Together app is running (default: 3149)")
args = parser.parse_args()

# API configuration
API_BASE_URL = f"http://localhost:{args.port}/api"
logger.info(f"Using API base URL: {API_BASE_URL}")

# Create an MCP server
logger.info("Creating MCP server")
mcp = FastMCP("Build Together")

# Helper to build data dict only with non-default values
def build_request_data(**kwargs):
    data = {}
    for key, value in kwargs.items():
        # Add checks for default values we want to omit
        if isinstance(value, str) and value: 
            data[key] = value
        elif isinstance(value, int) and value > 0: # Assuming 0 is default/omit for IDs
             data[key] = value
        elif isinstance(value, bool): # Always include booleans if passed
             data[key] = value
        # Add other specific default checks if needed
    return data

# ==================== PROJECT MANAGEMENT TOOLS ====================

@mcp.tool()
def get_projects() -> Dict[str, Any]:
    """Get a list of available projects to build together
    
    Returns:
        A dictionary with a list of projects
    """
    logger.info("Fetching projects from BuildTogether API")
    
    try:
        response = requests.get(f"{API_BASE_URL}/projects")
        response.raise_for_status()
        # Assuming API returns {"data": [...], "status": "success"}
        api_response = response.json()
        return {"projects": api_response.get("data", [])}
    except requests.RequestException as e:
        logger.error(f"Error fetching projects from API: {e}")
        return {"projects": []}
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding projects API response: {e}")
        return {"projects": []}

@mcp.tool()
def get_project_details(project_id: int) -> Dict[str, Any]:
    """Get detailed information about a specific project
    
    Args:
        project_id: The ID of the project to retrieve
        
    Returns:
        Project details including name, description, requirements, etc.
    """
    logger.info(f"Fetching details for project {project_id}")
    
    try:
        response = requests.get(f"{API_BASE_URL}/projects/{project_id}")
        response.raise_for_status()
        api_response = response.json()
        return {"project": api_response.get("data", {})}
    except requests.RequestException as e:
        logger.error(f"Error fetching project details: {e}")
        return {"error": str(e)}
    except json.JSONDecodeError as e:
         logger.error(f"Error decoding project details API response: {e}")
         return {"error": f"JSON Decode Error: {e}"}

@mcp.tool()
def create_project(name: str, description: str = "") -> Dict[str, Any]:
    """Create a new project
    
    Args:
        name: The name of the project
        description: Optional project description (provide empty string if none)
        
    Returns:
        The created project details
    """
    logger.info(f"Creating new project: {name}")
    
    try:
        # Use helper, description will be included if not empty
        data = build_request_data(name=name, description=description) 
        response = requests.post(f"{API_BASE_URL}/projects", json=data)
        response.raise_for_status()
        api_response = response.json()
        return {"project": api_response.get("data", {}), "message": "Project created successfully"}
    except requests.RequestException as e:
        logger.error(f"Error creating project: {e}")
        # Try to get more info from response if available
        error_details = str(e)
        try:
            error_details = response.json().get("error", error_details)
        except: pass
        return {"error": error_details}
    except json.JSONDecodeError as e:
         logger.error(f"Error decoding create project API response: {e}")
         return {"error": f"JSON Decode Error: {e}"}

@mcp.tool()
def update_project(project_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """Update a project with provided data dictionary.
    
    Args:
        project_id: The ID of the project to update
        data: Dictionary containing fields to update (name, description, etc.)
        
    Returns:
        The updated project details
    """
    logger.info(f"Updating project {project_id} with data: {data}")
    
    try:
        response = requests.put(f"{API_BASE_URL}/projects/{project_id}", json=data)
        response.raise_for_status()
        api_response = response.json()
        return {"project": api_response.get("data", {}), "message": "Project updated successfully"}
    except requests.RequestException as e:
        logger.error(f"Error updating project: {e}")
        error_details = str(e)
        try:
            error_details = response.json().get("error", error_details)
        except: pass
        return {"error": error_details}
    except json.JSONDecodeError as e:
         logger.error(f"Error decoding API response: {e}")
         return {"error": f"JSON Decode Error: {e}"}

@mcp.tool()
def delete_project(project_id: int) -> Dict[str, Any]:
    """Delete a project
    
    Args:
        project_id: The ID of the project to delete
        
    Returns:
        Success message or error
    """
    logger.info(f"Deleting project {project_id}")
    
    try:
        response = requests.delete(f"{API_BASE_URL}/projects/{project_id}")
        response.raise_for_status()
        # Assuming API returns success message or just 2xx status
        return {"message": f"Project {project_id} deleted successfully"}
    except requests.RequestException as e:
        logger.error(f"Error deleting project: {e}")
        error_details = str(e)
        try:
            error_details = response.json().get("error", error_details)
        except: pass
        return {"error": error_details}

# ==================== SPRINT MANAGEMENT TOOLS ====================

@mcp.tool()
def list_sprints(project_id: int = 0) -> Dict[str, Any]:
    """List all sprints, optionally filtered by project_id (use 0 for all).
    
    Args:
        project_id: Project ID to filter sprints (0 for all projects)
        
    Returns:
        List of sprints
    """
    url = f"{API_BASE_URL}/sprints"
    params = {}
    if project_id > 0:
        params['project_id'] = project_id
        logger.info(f"Fetching sprints for project {project_id}")
    else:
        logger.info("Fetching all sprints")
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        api_response = response.json()
        return {"sprints": api_response.get("data", [])}
    except requests.RequestException as e:
        logger.error(f"Error fetching sprints: {e}")
        return {"sprints": []}
    except json.JSONDecodeError as e:
         logger.error(f"Error decoding list sprints API response: {e}")
         return {"sprints": []}

@mcp.tool()
def get_sprint_details(sprint_id: int) -> Dict[str, Any]:
    """Get detailed information about a specific sprint
    
    Args:
        sprint_id: The ID of the sprint to retrieve
        
    Returns:
        Sprint details
    """
    logger.info(f"Fetching details for sprint {sprint_id}")
    
    try:
        response = requests.get(f"{API_BASE_URL}/sprints/{sprint_id}")
        response.raise_for_status()
        api_response = response.json()
        return {"sprint": api_response.get("data", {})}
    except requests.RequestException as e:
        logger.error(f"Error fetching sprint details: {e}")
        error_details = str(e)
        try:
            error_details = response.json().get("error", error_details)
        except: pass
        return {"error": error_details}
    except json.JSONDecodeError as e:
         logger.error(f"Error decoding get sprint details API response: {e}")
         return {"error": f"JSON Decode Error: {e}"}

@mcp.tool()
def create_sprint(
    name: str,
    project_id: int,
    description: str = "",
    status: str = "Planned" # Keep default, API validates
) -> Dict[str, Any]:
    """Create a new sprint
    
    Args:
        name: The name of the sprint
        project_id: The project this sprint belongs to
        description: Optional sprint description (provide empty string if none)
        status: Sprint status (Planned, Active, Completed) - defaults to Planned
        
    Returns:
        The created sprint details
    """
    logger.info(f"Creating new sprint '{name}' for project {project_id}")
    
    try:
        # Build data, including defaults if not overridden
        data = build_request_data(name=name, project_id=project_id, description=description, status=status)
        # Ensure required fields are present even if helper removed them
        if 'name' not in data: data['name'] = name
        if 'project_id' not in data: data['project_id'] = project_id
        if 'status' not in data: data['status'] = status # Send default if not provided

        response = requests.post(f"{API_BASE_URL}/sprints", json=data)
        response.raise_for_status()
        api_response = response.json()
        return {"sprint": api_response.get("data", {}), "message": "Sprint created successfully"}
    except requests.RequestException as e:
        logger.error(f"Error creating sprint: {e}")
        error_details = str(e)
        try:
            error_details = response.json().get("error", error_details)
        except: pass
        return {"error": error_details}
    except json.JSONDecodeError as e:
         logger.error(f"Error decoding create sprint API response: {e}")
         return {"error": f"JSON Decode Error: {e}"}

@mcp.tool()
def update_sprint(
    sprint_id: int,
    name: str = "",
    project_id: int = 0,
    description: str = "",
    status: str = "" # API validates status, empty means no change
) -> Dict[str, Any]:
    """Update an existing sprint. Only non-empty/non-zero fields are updated.
    
    Args:
        sprint_id: The ID of the sprint to update
        name: New name (leave empty to keep current)
        project_id: New project ID (leave 0 to keep current)
        description: New description (leave empty to keep current)
        status: New status (Planned, Active, Completed) (leave empty to keep current)
        
    Returns:
        The updated sprint details
    """
    logger.info(f"Updating sprint {sprint_id}")
    
    try:
        # First, fetch the current sprint details to get the required fields
        try:
            get_response = requests.get(f"{API_BASE_URL}/sprints/{sprint_id}")
            get_response.raise_for_status()
            current_sprint = get_response.json().get("data", {})
            
            if not current_sprint:
                return {"error": f"Sprint with ID {sprint_id} not found"}
                
            # Start with current values for required fields
            data = {
                "name": current_sprint.get("name", ""),
                "project_id": current_sprint.get("project_id", 0)
            }
            
            # Apply updates to the data
            if name:
                data["name"] = name
            if project_id > 0:
                data["project_id"] = project_id
            if description:
                data["description"] = description
            if status:
                data["status"] = status
                
            # Now we have a complete data object with all required fields
            
        except Exception as fetch_error:
            logger.error(f"Error fetching current sprint data: {fetch_error}")
            return {"error": f"Could not get current sprint data: {str(fetch_error)}"}

        # Send the update request with complete data
        response = requests.put(f"{API_BASE_URL}/sprints/{sprint_id}", json=data)
        response.raise_for_status()
        api_response = response.json()
        return {"sprint": api_response.get("data", {}), "message": "Sprint updated successfully"}
    except requests.RequestException as e:
        logger.error(f"Error updating sprint: {e}")
        error_details = str(e)
        try:
            error_details = response.json().get("error", error_details)
        except: pass
        return {"error": error_details}
    except json.JSONDecodeError as e:
         logger.error(f"Error decoding update sprint API response: {e}")
         return {"error": f"JSON Decode Error: {e}"}

@mcp.tool()
def delete_sprint(sprint_id: int) -> Dict[str, Any]:
    """Delete a sprint
    
    Args:
        sprint_id: The ID of the sprint to delete
        
    Returns:
        Success message or error
    """
    logger.info(f"Deleting sprint {sprint_id}")
    
    try:
        response = requests.delete(f"{API_BASE_URL}/sprints/{sprint_id}")
        response.raise_for_status()
        return {"message": f"Sprint {sprint_id} deleted successfully"}
    except requests.RequestException as e:
        logger.error(f"Error deleting sprint: {e}")
        error_details = str(e)
        try:
            error_details = response.json().get("error", error_details)
        except: pass
        return {"error": error_details}

# ==================== TASK MANAGEMENT TOOLS ====================

@mcp.tool()
def list_tasks(sprint_id: int = 0) -> Dict[str, Any]:
    """List all tasks, optionally filtered by sprint_id (use 0 for all).
    
    Args:
        sprint_id: Sprint ID to filter tasks (0 for all sprints)
        
    Returns:
        List of tasks
    """
    url = f"{API_BASE_URL}/tasks"
    params = {}
    if sprint_id > 0:
        params['sprint_id'] = sprint_id
        logger.info(f"Fetching tasks for sprint {sprint_id}")
    else:
        logger.info("Fetching all tasks")

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        api_response = response.json()
        return {"tasks": api_response.get("data", [])}
    except requests.RequestException as e:
        logger.error(f"Error fetching tasks: {e}")
        return {"tasks": []}
    except json.JSONDecodeError as e:
         logger.error(f"Error decoding list tasks API response: {e}")
         return {"tasks": []}

@mcp.tool()
def get_task_details(task_id: int) -> Dict[str, Any]:
    """Get detailed information about a specific task
    
    Args:
        task_id: The ID of the task to retrieve
        
    Returns:
        Task details
    """
    logger.info(f"Fetching details for task {task_id}")
    
    try:
        response = requests.get(f"{API_BASE_URL}/tasks/{task_id}")
        response.raise_for_status()
        api_response = response.json()
        return {"task": api_response.get("data", {})}
    except requests.RequestException as e:
        logger.error(f"Error fetching task details: {e}")
        error_details = str(e)
        try:
            error_details = response.json().get("error", error_details)
        except: pass
        return {"error": error_details}
    except json.JSONDecodeError as e:
         logger.error(f"Error decoding get task details API response: {e}")
         return {"error": f"JSON Decode Error: {e}"}

@mcp.tool()
def create_task(
    details: str,
    sprint_id: int,
    completed: bool = False # Default to False
) -> Dict[str, Any]:
    """Create a new task
    
    Args:
        details: The task details
        sprint_id: The sprint this task belongs to
        completed: Whether the task is completed (defaults to False)
        
    Returns:
        The created task details
    """
    logger.info(f"Creating new task in sprint {sprint_id}")
    
    try:
        # Use boolean directly
        data = {
            "details": details,
            "sprint_id": sprint_id,
            "completed": completed 
        }
            
        response = requests.post(f"{API_BASE_URL}/tasks", json=data)
        response.raise_for_status()
        api_response = response.json()
        return {"task": api_response.get("data", {}), "message": "Task created successfully"}
    except requests.RequestException as e:
        logger.error(f"Error creating task: {e}")
        error_details = str(e)
        try:
            error_details = response.json().get("error", error_details)
        except: pass
        return {"error": error_details}
    except json.JSONDecodeError as e:
         logger.error(f"Error decoding create task API response: {e}")
         return {"error": f"JSON Decode Error: {e}"}

@mcp.tool()
def update_task(
    task_id: int,
    details: str = "",
    sprint_id: int = 0,
    completed: bool = None # Use None to signify "no change" for boolean
) -> Dict[str, Any]:
    """Update an existing task. Only non-empty/non-zero/non-None fields are updated.
    
    Args:
        task_id: The ID of the task to update
        details: New details (leave empty to keep current)
        sprint_id: New sprint ID (leave 0 to keep current)
        completed: New completion status (True or False, leave None to keep current)
        
    Returns:
        The updated task details
    """
    logger.info(f"Updating task {task_id}")
    
    try:
        # Build data carefully, handling None for boolean
        data = {}
        if details:
            data['details'] = details
        if sprint_id > 0:
            data['sprint_id'] = sprint_id
        if completed is not None: # Only include if explicitly True or False
             data['completed'] = completed

        if not data:
            return {"message": "No update data provided."}
            
        response = requests.put(f"{API_BASE_URL}/tasks/{task_id}", json=data)
        response.raise_for_status()
        api_response = response.json()
        return {"task": api_response.get("data", {}), "message": "Task updated successfully"}
    except requests.RequestException as e:
        logger.error(f"Error updating task: {e}")
        error_details = str(e)
        try:
            error_details = response.json().get("error", error_details)
        except: pass
        return {"error": error_details}
    except json.JSONDecodeError as e:
         logger.error(f"Error decoding update task API response: {e}")
         return {"error": f"JSON Decode Error: {e}"}

@mcp.tool()
def complete_task(task_id: int) -> Dict[str, Any]:
    """Mark a task as completed
    
    Args:
        task_id: The ID of the task to complete
        
    Returns:
        The updated task details
    """
    logger.info(f"Marking task {task_id} as completed")
    
    try:
        data = {"completed": True} # Explicitly set completed to True
        response = requests.put(f"{API_BASE_URL}/tasks/{task_id}", json=data)
        response.raise_for_status()
        api_response = response.json()
        return {"task": api_response.get("data", {}), "message": "Task marked as completed"}
    except requests.RequestException as e:
        logger.error(f"Error completing task: {e}")
        error_details = str(e)
        try:
            error_details = response.json().get("error", error_details)
        except: pass
        return {"error": error_details}
    except json.JSONDecodeError as e:
         logger.error(f"Error decoding complete task API response: {e}")
         return {"error": f"JSON Decode Error: {e}"}

@mcp.tool()
def delete_task(task_id: int) -> Dict[str, Any]:
    """Delete a task
    
    Args:
        task_id: The ID of the task to delete
        
    Returns:
        Success message or error
    """
    logger.info(f"Deleting task {task_id}")
    
    try:
        response = requests.delete(f"{API_BASE_URL}/tasks/{task_id}")
        response.raise_for_status()
        return {"message": f"Task {task_id} deleted successfully"}
    except requests.RequestException as e:
        logger.error(f"Error deleting task: {e}")
        error_details = str(e)
        try:
            error_details = response.json().get("error", error_details)
        except: pass
        return {"error": error_details}

# ==================== ISSUE MANAGEMENT TOOLS ====================

@mcp.tool()
def list_issues(sprint_id: int = 0) -> Dict[str, Any]:
    """List all issues, optionally filtered by sprint_id (use 0 for all).
    
    Args:
        sprint_id: Sprint ID to filter issues (0 for all sprints)
        
    Returns:
        List of issues
    """
    url = f"{API_BASE_URL}/issues"
    params = {}
    if sprint_id > 0:
        params['sprint_id'] = sprint_id
        logger.info(f"Fetching issues for sprint {sprint_id}")
    else:
        logger.info("Fetching all issues")
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        api_response = response.json()
        return {"issues": api_response.get("data", [])}
    except requests.RequestException as e:
        logger.error(f"Error fetching issues: {e}")
        return {"issues": []}
    except json.JSONDecodeError as e:
         logger.error(f"Error decoding list issues API response: {e}")
         return {"issues": []}

@mcp.tool()
def get_issue_details(issue_id: int) -> Dict[str, Any]:
    """Get detailed information about a specific issue
    
    Args:
        issue_id: The ID of the issue to retrieve
        
    Returns:
        Issue details
    """
    logger.info(f"Fetching details for issue {issue_id}")
    
    try:
        response = requests.get(f"{API_BASE_URL}/issues/{issue_id}")
        response.raise_for_status()
        api_response = response.json()
        return {"issue": api_response.get("data", {})}
    except requests.RequestException as e:
        logger.error(f"Error fetching issue details: {e}")
        error_details = str(e)
        try:
            error_details = response.json().get("error", error_details)
        except: pass
        return {"error": error_details}
    except json.JSONDecodeError as e:
         logger.error(f"Error decoding get issue details API response: {e}")
         return {"error": f"JSON Decode Error: {e}"}

@mcp.tool()
def create_issue(
    details: str,
    sprint_id: int,
    completed: bool = False # Default to False
) -> Dict[str, Any]:
    """Create a new issue
    
    Args:
        details: The issue details
        sprint_id: The sprint this issue belongs to
        completed: Whether the issue is resolved (defaults to False)
        
    Returns:
        The created issue details
    """
    logger.info(f"Creating new issue in sprint {sprint_id}")
    
    try:
        data = {
            "details": details,
            "sprint_id": sprint_id,
            "completed": completed
        }
            
        response = requests.post(f"{API_BASE_URL}/issues", json=data)
        response.raise_for_status()
        api_response = response.json()
        return {"issue": api_response.get("data", {}), "message": "Issue created successfully"}
    except requests.RequestException as e:
        logger.error(f"Error creating issue: {e}")
        error_details = str(e)
        try:
            error_details = response.json().get("error", error_details)
        except: pass
        return {"error": error_details}
    except json.JSONDecodeError as e:
         logger.error(f"Error decoding create issue API response: {e}")
         return {"error": f"JSON Decode Error: {e}"}

@mcp.tool()
def update_issue(
    issue_id: int,
    details: str = "",
    sprint_id: int = 0,
    completed: bool = None # Use None to signify "no change" for boolean
) -> Dict[str, Any]:
    """Update an existing issue. Only non-empty/non-zero/non-None fields are updated.
    
    Args:
        issue_id: The ID of the issue to update
        details: New details (leave empty to keep current)
        sprint_id: New sprint ID (leave 0 to keep current)
        completed: New resolution status (True or False, leave None to keep current)
        
    Returns:
        The updated issue details
    """
    logger.info(f"Updating issue {issue_id}")
    
    try:
        data = {}
        if details:
            data['details'] = details
        if sprint_id > 0:
            data['sprint_id'] = sprint_id
        if completed is not None:
            data['completed'] = completed

        if not data:
             return {"message": "No update data provided."}
            
        response = requests.put(f"{API_BASE_URL}/issues/{issue_id}", json=data)
        response.raise_for_status()
        api_response = response.json()
        return {"issue": api_response.get("data", {}), "message": "Issue updated successfully"}
    except requests.RequestException as e:
        logger.error(f"Error updating issue: {e}")
        error_details = str(e)
        try:
            error_details = response.json().get("error", error_details)
        except: pass
        return {"error": error_details}
    except json.JSONDecodeError as e:
         logger.error(f"Error decoding update issue API response: {e}")
         return {"error": f"JSON Decode Error: {e}"}

@mcp.tool()
def resolve_issue(issue_id: int) -> Dict[str, Any]:
    """Mark an issue as resolved
    
    Args:
        issue_id: The ID of the issue to resolve
        
    Returns:
        The updated issue details
    """
    logger.info(f"Marking issue {issue_id} as resolved")
    
    try:
        data = {"completed": True} # Explicitly set completed to True
        response = requests.put(f"{API_BASE_URL}/issues/{issue_id}", json=data)
        response.raise_for_status()
        api_response = response.json()
        return {"issue": api_response.get("data", {}), "message": "Issue marked as resolved"}
    except requests.RequestException as e:
        logger.error(f"Error resolving issue: {e}")
        error_details = str(e)
        try:
            error_details = response.json().get("error", error_details)
        except: pass
        return {"error": error_details}
    except json.JSONDecodeError as e:
         logger.error(f"Error decoding resolve issue API response: {e}")
         return {"error": f"JSON Decode Error: {e}"}

@mcp.tool()
def delete_issue(issue_id: int) -> Dict[str, Any]:
    """Delete an issue
    
    Args:
        issue_id: The ID of the issue to delete
        
    Returns:
        Success message or error
    """
    logger.info(f"Deleting issue {issue_id}")
    
    try:
        response = requests.delete(f"{API_BASE_URL}/issues/{issue_id}")
        response.raise_for_status()
        return {"message": f"Issue {issue_id} deleted successfully"}
    except requests.RequestException as e:
        logger.error(f"Error deleting issue: {e}")
        error_details = str(e)
        try:
            error_details = response.json().get("error", error_details)
        except: pass
        return {"error": error_details}

# Run the server directly
if __name__ == "__main__":
    logger.info("Starting MCP server")
    try:
        # Run the server with default settings
        mcp.run()
    except Exception as e:
        logger.error(f"Error in MCP server: {e}")
        sys.exit(1) 