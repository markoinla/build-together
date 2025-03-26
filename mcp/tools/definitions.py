"""
MCP Tool Definitions

This module contains the definitions for all MCP tools used in the Build Together application.
It centralizes tool definitions to ensure consistency between the standalone MCP server
and the Flask application integration.

Each tool follows the Model Context Protocol (MCP) standard for tool definitions,
which includes a name, description, and input schema with proper validation rules.

IMPORTANT NOTES FOR AI ASSISTANTS:
1. When using these tools, do NOT include any prefix (like 'mcp0_') in the tool name
2. Only include parameters that are explicitly defined in the inputSchema
3. Do not include the 'status' parameter for list_projects unless filtering is needed
4. If you encounter errors, try simplifying your request by removing optional parameters
5. For tasks and issues, use the 'details' parameter (not 'title' or 'description')
"""

from typing import Dict, Any, Optional

# Tool definitions that can be imported by both the standalone MCP server
# and the Flask application integration
TOOLS = [
    {
        "name": "list_projects",
        "description": """List all projects in Build Together (BTG).
        
Example:
  Input: {}
  Output: List of all projects with their IDs, names, descriptions, and other details.
  
Use this tool to get an overview of all projects in the system.""",
        "inputSchema": {
            "type": "object",
            "properties": {
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
  Input: {"name": "Website Redesign", "description": "Redesign company website"}
  Output: Details of the newly created project including its assigned ID.
  
Only the name is required; description is optional. Do not include a status parameter.""",
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
                }
            },
            "required": ["name"]
        }
    },
    {
        "name": "update_project",
        "description": """Update an existing project's details.
        
Example:
  Input: {"project_id": 1, "name": "Updated Project Name", "description": "Updated description"}
  Output: Updated details of project #1.
  
Only the project_id is required; provide only the fields you want to update.""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "integer",
                    "description": "ID of the project to update"
                },
                "name": {
                    "type": "string",
                    "description": "New name of the project"
                },
                "description": {
                    "type": "string",
                    "description": "New description of the project"
                },
                "requirements": {
                    "type": "string",
                    "description": "New requirements for the project"
                },
                "implementation_details": {
                    "type": "string",
                    "description": "New implementation details for the project"
                }
            },
            "required": ["project_id"]
        }
    },
    {
        "name": "list_sprints",
        "description": """List all sprints for a specific project or all sprints if no project is specified.
        
Example:
  Input: {} or {"project_id": 1}
  Output: List of sprints with their IDs, names, descriptions, and statuses.
  
The project_id is optional. If provided, only sprints for that project will be listed.""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "integer",
                    "description": "Optional ID of the project to list sprints for"
                }
            }
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
  
The project_id and name are required; description and status are optional. Status defaults to 'Planned' if not specified.""",
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
                    "description": "Status of the sprint (defaults to 'Planned' if not specified)",
                    "enum": ["Planned", "Active", "Completed"]
                }
            },
            "required": ["project_id", "name"]
        }
    },
    {
        "name": "update_sprint",
        "description": """Update an existing sprint's details.
        
Example:
  Input: {"sprint_id": 5, "name": "Updated Sprint Name", "status": "Active"}
  Output: Updated details of sprint #5.
  
Only the sprint_id is required; provide only the fields you want to update.""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "sprint_id": {
                    "type": "integer",
                    "description": "ID of the sprint to update"
                },
                "name": {
                    "type": "string",
                    "description": "New name of the sprint"
                },
                "project_id": {
                    "type": "integer",
                    "description": "New project ID for the sprint"
                },
                "description": {
                    "type": "string",
                    "description": "New description of the sprint"
                },
                "status": {
                    "type": "string",
                    "description": "New status of the sprint",
                    "enum": ["Planned", "Active", "Completed"]
                }
            },
            "required": ["sprint_id"]
        }
    },
    {
        "name": "list_tasks",
        "description": """List all tasks for a specific sprint.
        
Example:
  Input: {"sprint_id": 5} or {"sprint_id": 5, "status": "In Progress"}
  Output: List of tasks for sprint #5 with their IDs, titles, descriptions, and statuses.
  
The sprint_id is required; status is optional and can be omitted to list all tasks.""",
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
        "name": "get_task",
        "description": """Get detailed information about a specific task.
        
Example:
  Input: {"task_id": 12}
  Output: Complete details of task #12 including title, description, status, and priority.
  
Use this tool when you need comprehensive information about a single task.""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "integer",
                    "description": "ID of the task to retrieve"
                }
            },
            "required": ["task_id"]
        }
    },
    {
        "name": "create_task",
        "description": """Create a new task within a sprint.
        
Example:
  Input: {"sprint_id": 5, "details": "Design homepage - Create mockups for homepage"}
  Output: Details of the newly created task including its assigned ID.
  
The sprint_id and details are required; status and priority are optional. Only include parameters that are needed.""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "sprint_id": {
                    "type": "integer",
                    "description": "ID of the sprint to create the task in"
                },
                "details": {
                    "type": "string",
                    "description": "Details of the task (required)"
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
                },
                "completed": {
                    "type": "boolean",
                    "description": "Whether the task is completed"
                }
            },
            "required": ["sprint_id", "details"]
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
                "details": {
                    "type": "string",
                    "description": "New details of the task"
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
                },
                "completed": {
                    "type": "boolean",
                    "description": "Whether the task is completed"
                }
            },
            "required": ["task_id"]
        }
    },
    {
        "name": "list_issues",
        "description": """List all issues or issues for a specific sprint.
        
Example:
  Input: {} or {"sprint_id": 5}
  Output: List of all issues or issues for sprint #5 with their IDs, details, and other information.
  
The sprint_id is optional. If provided, only issues for that sprint will be listed.""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "sprint_id": {
                    "type": "integer",
                    "description": "Optional ID of the sprint to list issues for"
                }
            }
        }
    },
    {
        "name": "get_issue",
        "description": """Get detailed information about a specific issue.
        
Example:
  Input: {"issue_id": 8}
  Output: Complete details of issue #8 including title, description, status, and severity.
  
Use this tool when you need comprehensive information about a single issue.""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "issue_id": {
                    "type": "integer",
                    "description": "ID of the issue to retrieve"
                }
            },
            "required": ["issue_id"]
        }
    },
    {
        "name": "create_issue",
        "description": """Create a new issue within a sprint.
        
Example:
  Input: {"sprint_id": 5, "details": "Bug in login feature - Users cannot log in", "severity": "High"}
  Output: Details of the newly created issue including its assigned ID.
  
The sprint_id and details are required; severity and status are optional. Only include parameters that are needed.""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "sprint_id": {
                    "type": "integer",
                    "description": "ID of the sprint to create the issue in"
                },
                "details": {
                    "type": "string",
                    "description": "Details of the issue (required)"
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
                },
                "completed": {
                    "type": "boolean",
                    "description": "Whether the issue is completed/resolved"
                }
            },
            "required": ["sprint_id", "details"]
        }
    },
    {
        "name": "update_issue",
        "description": """Update an existing issue.
        
Example:
  Input: {"issue_id": 8, "status": "Resolved"}
  Output: Updated details of issue #8 with the new status.
  
Only the issue_id is required; provide only the fields you want to update. This is useful for changing the status or severity of an issue.""",
        "inputSchema": {
            "type": "object",
            "properties": {
                "issue_id": {
                    "type": "integer",
                    "description": "ID of the issue to update"
                },
                "details": {
                    "type": "string",
                    "description": "New details of the issue"
                },
                "status": {
                    "type": "string",
                    "description": "New status of the issue",
                    "enum": ["Open", "In Progress", "Resolved"]
                },
                "severity": {
                    "type": "string",
                    "description": "New severity of the issue",
                    "enum": ["Low", "Medium", "High", "Critical"]
                },
                "completed": {
                    "type": "boolean",
                    "description": "Whether the issue is completed/resolved"
                }
            },
            "required": ["issue_id"]
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
