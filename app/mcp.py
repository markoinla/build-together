"""
MCP Server Setup for BTG

This module handles the integration between the BTG Flask application
and the MCP server implementation. It sets up the necessary routes and
connections for the MCP server to communicate with the application.
"""

from flask import Flask, Blueprint, request, jsonify
import importlib.util
import sys
import os

# Import the MCP tool definitions
try:
    from mcp.tools.definitions import TOOLS as MCP_TOOLS
except ImportError:
    # Fallback to API tools if MCP package is not available
    MCP_TOOLS = []

def setup_mcp_server(app: Flask) -> Flask:
    """
    Set up the MCP server integration with the Flask application
    
    Args:
        app: The Flask application instance
        
    Returns:
        The modified Flask application
    """
    # Add a blueprint for MCP-related routes
    mcp_bp = Blueprint('mcp', __name__)
    
    @mcp_bp.route('/mcp/execute', methods=['POST'])
    def execute_mcp_tool():
        """
        Execute an MCP tool through the API
        
        This endpoint receives tool execution requests from the MCP server,
        forwards them to the appropriate API endpoint, and returns the results.
        """
        # Get the tool name and parameters from the request
        data = request.get_json()
        
        if not data or "name" not in data:
            return jsonify({"error": "Invalid request: Missing tool name"}), 400
            
        tool_name = data.get("name")
        parameters = data.get("parameters", {})
        
        # Import and execute the API function
        try:
            # Import the module dynamically
            from app.api.api import TOOLS
            
            # Check if the tool exists
            if tool_name not in TOOLS:
                return jsonify({"error": f"Tool '{tool_name}' not found"}), 404
                
            # Get the tool function and call it with the parameters
            tool_func = TOOLS[tool_name]
            
            # Call the tool function
            if parameters:
                # Process boolean parameters to ensure proper type conversion
                processed_parameters = {}
                
                # Import tool definitions to check parameter types
                from app.api.api import get_tools
                tool_defs = get_tools().json
                
                # Find the tool definition to validate parameter types
                tool_def = next((t for t in tool_defs if t.get("name") == tool_name), None)
                
                if tool_def and "parameters" in tool_def:
                    # Process each parameter according to its defined type
                    param_defs = tool_def["parameters"]
                    
                    for param_name, param_value in parameters.items():
                        if param_name in param_defs:
                            param_type = param_defs[param_name].get("type")
                            
                            # Handle specific type conversions
                            if param_type == "boolean" and not isinstance(param_value, bool):
                                # Convert string or other representations to boolean
                                if isinstance(param_value, str):
                                    if param_value.lower() in ["true", "1", "yes"]:
                                        processed_parameters[param_name] = True
                                    elif param_value.lower() in ["false", "0", "no"]:
                                        processed_parameters[param_name] = False
                                    else:
                                        processed_parameters[param_name] = param_value
                                else:
                                    # Try to convert to boolean based on truthiness
                                    processed_parameters[param_name] = bool(param_value)
                            elif param_type == "integer" and not isinstance(param_value, int):
                                # Try to convert to integer
                                try:
                                    processed_parameters[param_name] = int(param_value)
                                except (ValueError, TypeError):
                                    processed_parameters[param_name] = param_value
                            else:
                                processed_parameters[param_name] = param_value
                        else:
                            # Pass through parameters not in the definition
                            processed_parameters[param_name] = param_value
                else:
                    # If no tool definition is found, use parameters as-is
                    processed_parameters = parameters
                
                # Log the processed parameters
                app.logger.info(f"Executing tool '{tool_name}' with processed parameters: {processed_parameters}")
                
                # Call the tool function with the processed parameters
                result = tool_func(**processed_parameters)
            else:
                result = tool_func()
                
            # Return the result
            return jsonify({"result": result})
            
        except Exception as e:
            # Return any errors
            return jsonify({"error": str(e)}), 500
    
    # Register the blueprint with the app
    app.register_blueprint(mcp_bp)
    
    # Log that the MCP server has been set up
    app.logger.info("MCP server integration has been set up")
    
    return app
