# Build Together MCP Server

This is a Model Context Protocol (MCP) server that integrates with the Build Together application, providing tools for managing projects, sprints, tasks, and issues programmatically.

## Overview

The Build Together MCP server provides a comprehensive set of tools for interacting with the Build Together application's API. It allows AI assistants to:

- Get lists of projects, sprints, tasks, and issues
- Create new resources
- Retrieve detailed information about specific resources
- Update existing resources
- Delete resources

## API Improvements

The server's API endpoints have been optimized for better RESTful design:

- Added separate validation schemas for update operations (`UpdateProjectSchema`, `UpdateSprintSchema`, `UpdateTaskSchema`, `UpdateIssueSchema`)
- Implemented partial updates that don't require all fields to be specified
- Improved error handling and responses

## Available MCP Tools

### Project Management
- `get_projects` - Get list of all projects
- `get_project_details` - Get detailed information about a specific project
- `create_project` - Create a new project
- `update_project` - Update a project with a data dictionary
- `delete_project` - Delete a project

### Sprint Management
- `list_sprints` - List all sprints, optionally filtered by project ID
- `get_sprint_details` - Get detailed information about a specific sprint
- `create_sprint` - Create a new sprint
- `update_sprint` - Update an existing sprint
- `delete_sprint` - Delete a sprint

### Task Management
- `list_tasks` - List all tasks, optionally filtered by sprint ID
- `get_task_details` - Get detailed information about a specific task
- `create_task` - Create a new task
- `update_task` - Update an existing task
- `complete_task` - Mark a task as completed
- `delete_task` - Delete a task

### Issue Management
- `list_issues` - List all issues, optionally filtered by sprint ID
- `get_issue_details` - Get detailed information about a specific issue
- `create_issue` - Create a new issue
- `update_issue` - Update an existing issue
- `resolve_issue` - Mark an issue as resolved
- `delete_issue` - Delete an issue

## Running the Server

You can run the server directly with:

```bash
# Basic usage with default settings
./run_mcp.sh

# Format: ./run_mcp.sh [PORT] [AUTO_START]

# Connect to the Build Together app on port 8080
./run_mcp.sh 8080

# Connect to the Build Together app on default port but disable auto-start
./run_mcp.sh 3149 false

# Connect to the Build Together app on port 8080 with auto-start disabled
./run_mcp.sh 8080 false
```

The server provides the following features:
- Auto-detects if Build Together is already running
- Automatically starts Build Together if not running (can be disabled)
- Connects to the specified port for API communication
- Creates a virtual environment and installs dependencies if needed

The port parameter specifies which port the MCP server should use to communicate with the Build Together application - it does not change the port of the MCP server itself.

## Integration with Claude

To use this MCP server with Claude:

1. Make sure the Build Together application is running (uses port 3149 by default) - or rely on the auto-start feature
2. Add the MCP server to your Claude configuration

For Claude in Cursor:
- Configure Cursor to use the MCP server with path to the `run_mcp.sh` script

For Claude Desktop:
```json
{
    "mcpServers": {
        "buildTogether": {
            "command": "/absolute/path/to/mcp/run_mcp.sh",
            "args": ["3149", "true"],  # [port, auto-start]
            "env": {
                "PYTHONUNBUFFERED": "1",
                "PYTHONIOENCODING": "utf-8",
                "BTG_BASE_URL": "http://127.0.0.1:3149"
            }
        }
    }
}
```

Replace `/absolute/path/to/mcp/run_mcp.sh` with the actual path to the script. If your Build Together app runs on a different port, pass that port as the first argument in the `args` array and update the port in the `BTG_BASE_URL` environment variable to match. The second argument controls whether the MCP server will automatically start Build Together if it's not already running.

## Tool Usage Examples

Here are some examples of how to use the MCP tools with Claude:

- "Show me all the projects in Build Together"
- "Create a new sprint for project 1 called 'Sprint 5: API Integration'"
- "Mark task 12 as completed"
- "Update the details of issue 5 to mention that we've found a solution"
- "Delete sprint 6" 