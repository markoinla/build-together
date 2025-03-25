"""
MCP Tool Definitions

This module contains the definitions for all MCP tools used in the Build Together application.
It centralizes tool definitions to ensure consistency between the standalone MCP server
and the Flask application integration.

Each tool follows the Model Context Protocol (MCP) standard for tool definitions,
which includes a name, description, and input schema with proper validation rules.
"""

from typing import Dict, Any, Optional

# Tool definitions that can be imported by both the standalone MCP server
# and the Flask application integration
TOOLS = [
    {
        "name": "list_projects",
        "description": """List all projects in Build Together (BTG).
        
Example:
  Input: {"status": "Active"}
  Output: List of active projects with their IDs, names, descriptions, and statuses.
  
Use this tool to get an overview of projects in the system, filtered by their status if needed.""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "description": "Filter projects by status (Active, Completed, All)",
                    "enum": ["Active", "Completed", "All"]
                }
            }
        }
    },
    {
        "name": "get_project",
        "description": """Get detailed information about a specific project.
        
Example:
  Input: {"project_id": 1}
  Output: Complete details of project #1 including name, description, status, and creation date.
  
Use this tool when you need comprehensive information about a single project.""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "integer",
                    "description": "ID of the project to retrieve"
                }
            },
            "required": ["project_id"]
        }
    },
    {
        "name": "create_project",
        "description": """Create a new project in Build Together.
        
Example:
  Input: {"name": "Website Redesign", "description": "Redesign company website", "status": "Active"}
  Output: Details of the newly created project including its assigned ID.
  
Only the name is required; description and status are optional (status defaults to 'Active').""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the project"
                },
                "description": {
                    "type": "string",
                    "description": "Description of the project"
                },
                "status": {
                    "type": "string",
                    "description": "Status of the project (Active or Completed)",
                    "enum": ["Active", "Completed"]
                }
            },
            "required": ["name"]
        }
    },
    {
        "name": "list_sprints",
        "description": """List all sprints for a specific project.
        
Example:
  Input: {"project_id": 1, "status": "Active"}
  Output: List of active sprints for project #1 with their IDs, names, descriptions, and statuses.
  
Use this tool to view all sprints within a project, optionally filtered by status.""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "integer",
                    "description": "ID of the project to list sprints for"
                },
                "status": {
                    "type": "string",
                    "description": "Filter sprints by status",
                    "enum": ["Planned", "Active", "Completed", "All"]
                }
            },
            "required": ["project_id"]
        }
    },
    {
        "name": "get_sprint",
        "description": """Get detailed information about a specific sprint.
        
Example:
  Input: {"sprint_id": 5}
  Output: Complete details of sprint #5 including name, description, status, and associated project.
  
Use this tool when you need comprehensive information about a single sprint.""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "sprint_id": {
                    "type": "integer",
                    "description": "ID of the sprint to retrieve"
                }
            },
            "required": ["sprint_id"]
        }
    },
    {
        "name": "create_sprint",
        "description": """Create a new sprint within a project.
        
Example:
  Input: {"project_id": 1, "name": "Sprint 1", "description": "Initial development phase", "status": "Planned"}
  Output: Details of the newly created sprint including its assigned ID.
  
The project_id and name are required; description and status are optional (status defaults to 'Planned').""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "integer",
                    "description": "ID of the project to create the sprint in"
                },
                "name": {
                    "type": "string",
                    "description": "Name of the sprint"
                },
                "description": {
                    "type": "string",
                    "description": "Description of the sprint"
                },
                "status": {
                    "type": "string",
                    "description": "Status of the sprint",
                    "enum": ["Planned", "Active", "Completed"]
                }
            },
            "required": ["project_id", "name"]
        }
    },
    {
        "name": "list_tasks",
        "description": """List all tasks for a specific sprint.
        
Example:
  Input: {"sprint_id": 5, "status": "In Progress"}
  Output: List of in-progress tasks for sprint #5 with their IDs, titles, descriptions, and statuses.
  
Use this tool to view all tasks within a sprint, optionally filtered by status.""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "sprint_id": {
                    "type": "integer",
                    "description": "ID of the sprint to list tasks for"
                },
                "status": {
                    "type": "string",
                    "description": "Filter tasks by status",
                    "enum": ["Todo", "In Progress", "Done", "All"]
                }
            },
            "required": ["sprint_id"]
        }
    },
    {
        "name": "create_task",
        "description": """Create a new task within a sprint.
        
Example:
  Input: {"sprint_id": 5, "title": "Design homepage", "description": "Create mockups for homepage", "status": "Todo", "priority": "High"}
  Output: Details of the newly created task including its assigned ID.
  
The sprint_id and title are required; description, status, and priority are optional (status defaults to 'Todo', priority to 'Medium').""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "sprint_id": {
                    "type": "integer",
                    "description": "ID of the sprint to create the task in"
                },
                "title": {
                    "type": "string",
                    "description": "Title of the task"
                },
                "description": {
                    "type": "string",
                    "description": "Description of the task"
                },
                "status": {
                    "type": "string",
                    "description": "Status of the task",
                    "enum": ["Todo", "In Progress", "Done"]
                },
                "priority": {
                    "type": "string",
                    "description": "Priority of the task",
                    "enum": ["Low", "Medium", "High"]
                }
            },
            "required": ["sprint_id", "title"]
        }
    },
    {
        "name": "update_task",
        "description": """Update an existing task.
        
Example:
  Input: {"task_id": 12, "status": "Done"}
  Output: Updated details of task #12 with the new status.
  
Only the task_id is required; provide only the fields you want to update. This is useful for marking tasks as complete or changing their priority.""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "integer",
                    "description": "ID of the task to update"
                },
                "title": {
                    "type": "string",
                    "description": "New title of the task"
                },
                "description": {
                    "type": "string",
                    "description": "New description of the task"
                },
                "status": {
                    "type": "string",
                    "description": "New status of the task",
                    "enum": ["Todo", "In Progress", "Done"]
                },
                "priority": {
                    "type": "string",
                    "description": "New priority of the task",
                    "enum": ["Low", "Medium", "High"]
                }
            },
            "required": ["task_id"]
        }
    },
    {
        "name": "list_issues",
        "description": """List all issues for a sprint.
        
Example:
  Input: {"sprint_id": 5, "status": "Open"}
  Output: List of open issues for sprint #5 with their IDs, titles, descriptions, and statuses.
  
Use this tool to view all issues within a sprint, optionally filtered by status.""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "sprint_id": {
                    "type": "integer",
                    "description": "ID of the sprint to list issues for"
                },
                "status": {
                    "type": "string",
                    "description": "Filter issues by status",
                    "enum": ["Open", "In Progress", "Resolved", "All"]
                }
            },
            "required": ["sprint_id"]
        }
    },
    {
        "name": "create_issue",
        "description": """Create a new issue within a sprint.
        
Example:
  Input: {"sprint_id": 5, "title": "Bug in login feature", "description": "Users cannot log in", "status": "Open", "severity": "High"}
  Output: Details of the newly created issue including its assigned ID.
  
The sprint_id and title are required; description, status, and severity are optional (status defaults to 'Open', severity to 'Medium').""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "sprint_id": {
                    "type": "integer",
                    "description": "ID of the sprint to create the issue in"
                },
                "title": {
                    "type": "string",
                    "description": "Title of the issue"
                },
                "description": {
                    "type": "string",
                    "description": "Description of the issue"
                },
                "status": {
                    "type": "string",
                    "description": "Status of the issue",
                    "enum": ["Open", "In Progress", "Resolved"]
                },
                "severity": {
                    "type": "string",
                    "description": "Severity of the issue",
                    "enum": ["Low", "Medium", "High", "Critical"]
                }
            },
            "required": ["sprint_id", "title"]
        }
    }
]

def get_tool_definition(tool_name: str) -> Optional[Dict[str, Any]]:
    """
    Get the definition for a specific tool
    
    Args:
        tool_name: Name of the tool to get the definition for
        
    Returns:
        The tool definition or None if not found
    """
    for tool in TOOLS:
        if tool["name"] == tool_name:
            return tool
    return None

def get_tool_parameters(tool_name: str) -> Optional[Dict[str, Any]]:
    """
    Get the parameters for a specific tool
    
    Args:
        tool_name: Name of the tool to get the parameters for
        
    Returns:
        The tool parameters or None if not found
    """
    tool = get_tool_definition(tool_name)
    if tool and "inputSchema" in tool:
        return tool["inputSchema"].get("properties", {})
    return None
