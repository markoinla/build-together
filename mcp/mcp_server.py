#!/usr/bin/env python3
"""
Simple MCP Server for Build Together integration with Windsurf

This server implements the Model Context Protocol (MCP) using stdio transport
to integrate with Windsurf. It provides tools for interacting with the
Build Together application API.
"""

import os
import sys
import json
import logging
import asyncio
import httpx
import time
import signal
import threading
import traceback
from asyncio import TimeoutError as AsyncTimeoutError
from typing import Dict, Any, Optional, TextIO

# Setup logging to file for debugging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)

# Add the parent directory to the path so we can import the mcp package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import tool definitions from the mcp package
from mcp.tools.definitions import TOOLS, get_tool_definition, get_tool_parameters

# Create a logger for the MCP server
logger = logging.getLogger("buildtogether_mcp")

# Define API URL for the Build Together (BTG) API
BTG_API_URL = os.environ.get("BTG_BASE_URL", "http://127.0.0.1:3149") + "/mcp"

logger.info(f"Using Build Together API URL: {BTG_API_URL}")

# Configuration settings
CONFIG = {
    "request_timeout": 10.0,      # Overall timeout for requests
    "http_timeout": 5.0,          # HTTP request timeout
    "max_retries": 5,             # Maximum number of retries
    "ping_interval": 15,          # Seconds between keepalive pings
    "max_inactivity": 30,         # Maximum inactivity before potential hang
    "max_empty_inputs": 50,       # Threshold for empty inputs warning
    "rate_limit": {               # Rate limiting settings
        "enabled": True,
        "max_requests": 30,       # Maximum requests per minute
        "window_seconds": 60      # Time window for rate limiting
    }
}

# Track rate limiting
class RateLimiter:
    """Rate limiter to prevent abuse"""
    
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = []
        self.lock = threading.Lock()
    
    def check_rate_limit(self) -> bool:
        """Check if the current request is rate limited
        
        Returns:
            True if the request is allowed, False if rate limited
        """
        with self.lock:
            # Remove old requests outside the window
            current_time = time.time()
            self.requests = [t for t in self.requests if current_time - t < self.window_seconds]
            
            # Check if we've reached the limit
            if len(self.requests) >= self.max_requests:
                return False
            
            # Add the current request
            self.requests.append(current_time)
            return True

# Create a rate limiter
rate_limiter = RateLimiter(
    CONFIG["rate_limit"]["max_requests"],
    CONFIG["rate_limit"]["window_seconds"]
)

# Helper function to format error responses according to MCP best practices
def format_error_response(message: str, code: int = 500, data: Any = None) -> Dict[str, Any]:
    """Format an error response according to MCP best practices
    
    Args:
        message: Error message
        code: Error code
        data: Additional error data
        
    Returns:
        Formatted error response
    """
    return {
        "isError": True,
        "error": {
            "code": code,
            "message": message,
            "data": data
        },
        "content": [
            {
                "type": "text",
                "text": f"Error: {message}"
            }
        ]
    }

async def execute_tool(tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a tool with the given parameters
    
    Args:
        tool_name: The name of the tool to execute
        parameters: The parameters to pass to the tool
        
    Returns:
        The result of executing the tool
    """
    # Generate a unique request ID for tracking
    request_id = f"{int(time.time())}-{hash(tool_name)}"
    
    try:
        # First, send a ping to establish the connection
        try:
            async with httpx.AsyncClient() as client:
                ping_response = await client.get(f"{BTG_API_URL}/ping", timeout=2.0)
                logger.debug(f"[{request_id}] Ping response: {ping_response.status_code}")
        except Exception as e:
            logger.warning(f"[{request_id}] Ping failed, but continuing: {e}")
            # Continue anyway, since the main request might still work
        
        # Log the request for debugging
        logger.info(f"[{request_id}] Executing tool: {tool_name} with parameters: {parameters}")
        
        # Find the tool definition
        tool_def = next((t for t in TOOLS if t["name"] == tool_name), None)
        
        if tool_def:
            logger.info(f"[{request_id}] Found tool definition for '{tool_name}'")
            # Process each parameter according to its defined type
            if "inputSchema" in tool_def:
                # Get required parameters if defined
                required_params = tool_def["inputSchema"].get("required", [])
                
                # Check if all required parameters are present
                missing_params = [p for p in required_params if p not in parameters]
                if missing_params:
                    return format_error_response(
                        f"Missing required parameters: {', '.join(missing_params)}", 400
                    )
                    
                # Process each parameter according to its defined type
                param_defs = tool_def["inputSchema"].get("properties", {})
                for param_name, param_value in parameters.items():
                    if param_name in param_defs:
                        param_type = param_defs[param_name].get("type")
                        
                        # Basic type conversion
                        if param_type == "integer" and not isinstance(param_value, int):
                            try:
                                parameters[param_name] = int(param_value)
                            except (ValueError, TypeError):
                                return format_error_response(
                                    f"Parameter '{param_name}' must be an integer", 400
                                )
                        elif param_type == "number" and not isinstance(param_value, (int, float)):
                            try:
                                parameters[param_name] = float(param_value)
                            except (ValueError, TypeError):
                                return format_error_response(
                                    f"Parameter '{param_name}' must be a number", 400
                                )
                        elif param_type == "boolean" and not isinstance(param_value, bool):
                            if param_value in ["true", "True", "1", 1]:
                                parameters[param_name] = True
                            elif param_value in ["false", "False", "0", 0]:
                                parameters[param_name] = False
                            else:
                                return format_error_response(
                                    f"Parameter '{param_name}' must be a boolean", 400
                                )
        else:
            logger.error(f"[{request_id}] Tool '{tool_name}' not found")
            return format_error_response(f"Tool '{tool_name}' not found", 404)
        
        # Apply rate limiting if enabled
        if CONFIG["rate_limit"]["enabled"]:
            if not rate_limiter.check_rate_limit():
                logger.warning(f"[{request_id}] Rate limit exceeded for tool: {tool_name}")
                return format_error_response("Rate limit exceeded. Please try again later.", 429)
        
        # Execute the tool against the Build Together API
        # Important: We're calling /execute endpoint instead of /tools/{tool_name}
        url = f"{BTG_API_URL}/execute"
        
        try:
            # Format the request according to what the Flask app expects
            request_data = {
                "name": tool_name,
                "parameters": parameters
            }
            
            logger.debug(f"[{request_id}] Sending request to {url} with data: {request_data}")
            
            # Make the API request with timeout
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url, 
                    json=request_data,
                    timeout=CONFIG["http_timeout"]
                )
            
            # Check for HTTP errors
            if response.status_code >= 400:
                logger.error(f"[{request_id}] API error: {response.status_code} {response.text}")
                
                # Try to parse the error response
                try:
                    error_json = response.json()
                    error_message = error_json.get("error", "Unknown error")
                except Exception:
                    error_message = response.text or f"HTTP error {response.status_code}"
                    
                return format_error_response(error_message, response.status_code)
            
            # Parse the response
            result = response.json()
            logger.debug(f"[{request_id}] API response: {result}")
            
            # Log success
            logger.info(f"[{request_id}] Tool execution successful")
            
            # Check if the result is already in the expected format
            if "result" in result:
                # The Flask app returns {"result": actual_data}
                actual_result = result["result"]
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(actual_result)
                        }
                    ],
                    "isError": False
                }
            else:
                # Something else was returned
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result)
                        }
                    ],
                    "isError": False
                }
            
        except httpx.TimeoutException:
            logger.error(f"[{request_id}] Request timed out for tool: {tool_name}")
            return format_error_response("Request timed out", 408)
            
        except Exception as e:
            logger.error(f"[{request_id}] Error executing tool: {str(e)}")
            logger.error(traceback.format_exc())
            return format_error_response(f"Error executing tool: {str(e)}")
    
    except Exception as e:
        # Catch-all for any unexpected errors
        logger.error(f"[{request_id}] Unexpected error: {str(e)}")
        logger.error(traceback.format_exc())
        return format_error_response(f"Unexpected error: {str(e)}")

class StdioTransport:
    """A more robust implementation of stdio transport for MCP"""
    
    def __init__(self, stdin: TextIO = sys.stdin, stdout: TextIO = sys.stdout):
        """Initialize the transport
        
        Args:
            stdin: Input stream
            stdout: Output stream
        """
        self.stdin = stdin
        self.stdout = stdout
        self.read_buffer = ""
        self.buffer_lock = threading.Lock()
        self.is_running = True
        self.data_received_event = threading.Event()  # Event to signal new data
        self.last_activity_time = time.time()  # Track when we last saw activity
        self.message_counter = 0  # Track received messages for diagnostics
        self.empty_inputs_count = 0  # Track consecutive empty inputs
        self.health_check_interval = CONFIG["ping_interval"]  # Seconds between health checks
        
        # Start background tasks
        self.read_thread = threading.Thread(target=self._read_stdin_loop, daemon=True)
        self.keep_alive_thread = threading.Thread(target=self._keep_alive_loop, daemon=True)
        
        # Create an event for connection restore/reset
        self.connection_reset_event = threading.Event()
        
        # Start the watchdog timer for connection health monitoring
        self.watchdog_thread = threading.Thread(target=self._watchdog_loop, daemon=True)
    
    def start(self):
        """Start the transport threads"""
        logger.info("Starting StdioTransport")
        self.read_thread.start()
        self.keep_alive_thread.start()
        self.watchdog_thread.start()
    
    def _read_stdin_loop(self):
        """Background thread to continuously read from stdin"""
        logger.info("StdioTransport read thread started")
        
        while self.is_running:
            try:
                line = self.stdin.readline()
                
                if not line:
                    # Handle the case of empty input (potential EOF or disconnect)
                    self.empty_inputs_count += 1
                    if self.empty_inputs_count >= CONFIG["max_empty_inputs"]:
                        logger.warning(
                            f"Received {self.empty_inputs_count} consecutive empty inputs. "
                            "Potential disconnection from client."
                        )
                    
                    # Short sleep to prevent CPU spinning on EOF
                    time.sleep(0.01)
                    continue
                
                # Reset counter on successful read
                self.empty_inputs_count = 0
                
                # Update last activity time
                self.last_activity_time = time.time()
                
                # Process the received line
                with self.buffer_lock:
                    self.read_buffer += line
                    
                    # Log the received data for debugging
                    logger.debug(f"Received data: {line.strip()}")
                    
                    # Increment message counter for diagnostics
                    self.message_counter += 1
                    
                    # Set event to notify waiting threads
                    self.data_received_event.set()
            except Exception as e:
                logger.error(f"Error reading from stdin: {str(e)}")
                logger.error(traceback.format_exc())
                time.sleep(0.1)  # Prevent tight looping on error
    
    def _keep_alive_loop(self):
        """Background thread to keep the connection alive by sending pings periodically"""
        logger.info("StdioTransport keep-alive thread started")
        
        while self.is_running:
            try:
                # Sleep for the configured interval
                time.sleep(self.health_check_interval)
                
                # Check if we need to send a keepalive ping
                # Only do this if there's been no activity for a while
                current_time = time.time()
                time_since_activity = current_time - self.last_activity_time
                
                if time_since_activity >= self.health_check_interval:
                    logger.debug(f"Sending keepalive ping after {time_since_activity:.1f}s of inactivity")
                    
                    # Send a ping notification to keep the connection alive
                    notification = {
                        "jsonrpc": "2.0",
                        "method": "notifications/ping",
                        "params": {
                            "timestamp": current_time
                        }
                    }
                    
                    try:
                        self._send_message(notification)
                        # Update the activity time after sending the ping
                        self.last_activity_time = current_time
                    except Exception as e:
                        logger.error(f"Failed to send keepalive ping: {str(e)}")
            except Exception as e:
                logger.error(f"Error in keep-alive loop: {str(e)}")
                logger.error(traceback.format_exc())
    
    def _watchdog_loop(self):
        """Background thread to monitor the connection health and reset if needed"""
        logger.info("StdioTransport watchdog thread started")
        
        while self.is_running:
            try:
                # Sleep for a period
                time.sleep(5)  # Check every 5 seconds
                
                # Check if connection has been inactive for too long
                current_time = time.time()
                inactivity_time = current_time - self.last_activity_time
                
                if inactivity_time > CONFIG["max_inactivity"]:
                    logger.warning(
                        f"Connection inactive for {inactivity_time:.1f}s, "
                        f"exceeding threshold of {CONFIG['max_inactivity']}s. "
                        "Triggering connection reset."
                    )
                    
                    # Set the connection reset event to trigger a reset
                    self.connection_reset_event.set()
                    
                    # Reset the last activity time to prevent multiple resets
                    self.last_activity_time = current_time
            except Exception as e:
                logger.error(f"Error in watchdog loop: {str(e)}")
                logger.error(traceback.format_exc())
    
    def _validate_jsonrpc_message(self, message: Dict[str, Any]) -> bool:
        """Validate a JSON-RPC message
        
        Args:
            message: The message to validate
            
        Returns:
            True if the message is valid, False otherwise
        """
        # Check if we have the required jsonrpc version
        if message.get("jsonrpc") != "2.0":
            logger.warning(f"Invalid jsonrpc version: {message.get('jsonrpc')}")
            return False
        
        # Check if we have either a method (for requests/notifications) or a result/error (for responses)
        if "method" in message:
            # It's a request or notification
            if not isinstance(message["method"], str):
                logger.warning(f"Invalid method type: {type(message['method'])}")
                return False
                
            # Request must have an id, notification must not
            if "id" in message:
                # It's a request, should have an id that's a string or number
                if not isinstance(message["id"], (str, int, float)):
                    logger.warning(f"Invalid request id type: {type(message['id'])}")
                    return False
            
            # Both requests and notifications can have params
            if "params" in message and not isinstance(message["params"], (dict, list)):
                logger.warning(f"Invalid params type: {type(message['params'])}")
                return False
        elif "id" in message:
            # It's a response, should have either result or error
            if "result" not in message and "error" not in message:
                logger.warning("Response missing both result and error")
                return False
                
            if "error" in message:
                error = message["error"]
                if not isinstance(error, dict):
                    logger.warning(f"Invalid error type: {type(error)}")
                    return False
                    
                if "code" not in error or not isinstance(error["code"], int):
                    logger.warning("Missing or invalid error code")
                    return False
                    
                if "message" not in error or not isinstance(error["message"], str):
                    logger.warning("Missing or invalid error message")
                    return False
        else:
            # Not a valid JSON-RPC message
            logger.warning("Message is neither a request, notification, nor response")
            return False
            
        return True
    
    def _send_message(self, message: Dict[str, Any]):
        """Send a message to the client
        
        Args:
            message: The message to send
        """
        try:
            # Validate the message before sending
            if not self._validate_jsonrpc_message(message):
                logger.error(f"Attempting to send invalid JSON-RPC message: {message}")
                # We'll still send it though to maintain compatibility
            
            # Serialize the message to JSON
            json_str = json.dumps(message)
            
            # Send the message to stdout
            self.stdout.write(json_str + "\n")
            self.stdout.flush()
            
            # Log the sent message for debugging
            if "method" in message and message["method"] == "notifications/ping":
                logger.debug("Sent keepalive ping")
            else:
                logger.debug(f"Sent message: {json_str}")
                
            # Update the activity timestamp
            self.last_activity_time = time.time()
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            logger.error(traceback.format_exc())
    
    def read_message(self) -> Optional[Dict[str, Any]]:
        """Read a message from the client
        
        Returns:
            The message as a dict, or None if no message is available
        """
        # First, see if we need to handle a connection reset
        if self.connection_reset_event.is_set():
            logger.info("Handling connection reset")
            # Clear any pending input
            with self.buffer_lock:
                self.read_buffer = ""
            # Reset the event
            self.connection_reset_event.clear()
            # Return None to indicate no message
            return None
            
        # Check if we have a complete message in the buffer
        with self.buffer_lock:
            if not self.read_buffer:
                return None
                
            try:
                # Try to parse the buffer as JSON
                message = json.loads(self.read_buffer)
                
                # If we got here, parsing succeeded - clear the buffer
                self.read_buffer = ""
                
                # Validate the message structure
                if not self._validate_jsonrpc_message(message):
                    logger.warning(f"Received invalid JSON-RPC message: {message}")
                    # We'll still process it though for compatibility
                
                # Return the parsed message
                return message
            except json.JSONDecodeError:
                # Not a complete JSON object yet, wait for more data
                return None
            except Exception as e:
                # Some other error occurred
                logger.error(f"Error parsing message: {str(e)}")
                logger.error(traceback.format_exc())
                
                # Clear the buffer to prevent getting stuck
                self.read_buffer = ""
                return None
    
    def wait_for_message(self, timeout: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """Wait for a message to arrive
        
        Args:
            timeout: Optional timeout in seconds
            
        Returns:
            The message as a dict, or None if timeout occurs
        """
        # First, try to read a message that might already be in the buffer
        message = self.read_message()
        if message:
            return message
            
        # If no message, wait for the data_received_event
        # Reset the event before waiting
        self.data_received_event.clear()
        
        # Wait for the event with timeout
        if self.data_received_event.wait(timeout):
            # If event was set, try to read a message again
            return self.read_message()
        else:
            # Timeout occurred
            return None
    
    def stop(self):
        """Stop the transport"""
        logger.info("Stopping StdioTransport")
        self.is_running = False
        
        # Clean up resources
        self.read_buffer = ""
        
        # Log diagnostics 
        logger.info(f"StdioTransport processed {self.message_counter} messages before shutdown")

async def handle_jsonrpc_request(message: Dict[str, Any]) -> None:
    """Handle a JSON-RPC request
    
    Args:
        message: The JSON-RPC request message
    """
    # Validate basic structure
    if "jsonrpc" not in message or message["jsonrpc"] != "2.0":
        logger.error(f"Invalid JSON-RPC version: {message.get('jsonrpc')}")
        await send_jsonrpc_error(
            message.get("id"),
            -32600,  # Invalid request
            "Invalid JSON-RPC version"
        )
        return
        
    if "method" not in message:
        logger.error("Missing method in JSON-RPC request")
        await send_jsonrpc_error(
            message.get("id"),
            -32600,  # Invalid request
            "Missing method"
        )
        return
        
    method = message["method"]
    params = message.get("params", {})
    request_id = message.get("id")
    
    # Log the received request for debugging
    logger.info(f"Handling JSON-RPC request: method={method}, id={request_id}")
    
    # Check if this is a notification (no id)
    is_notification = "id" not in message
    
    try:
        # Handle different method types
        if method == "reset_context":
            # Handle reset context request
            logger.info("Received reset_context request")
            
            # For now, we just acknowledge it
            if not is_notification:
                await send_jsonrpc_response(request_id, {"success": True})
        
        elif method == "call_tool" or method == "tools/call":
            # Extract the tool name and parameters
            if not isinstance(params, dict):
                logger.error(f"Invalid parameters for tool call: {params}")
                await send_jsonrpc_error(
                    request_id,
                    -32602,  # Invalid params
                    "Parameters must be an object"
                )
                return
                
            tool_name = params.get("name", "")
            tool_parameters = params.get("arguments", {})
            
            logger.info(f"Tool call request: {tool_name}")
            
            if not tool_name:
                logger.error("Missing tool name in tool call request")
                await send_jsonrpc_error(
                    request_id,
                    -32602,  # Invalid params
                    "Missing tool name"
                )
                return
            
            # Handle tool name prefixes more robustly
            original_tool_name = tool_name
            normalized_tools_map = {}
            
            # Create a mapping of normalized tool names (without prefixes) to full tool names
            for tool in TOOLS:
                t_name = tool.get("name", "")
                t_normalized = t_name
                
                # Remove common prefixes for comparison
                if t_normalized.startswith("mcp0_"):
                    t_normalized = t_normalized[5:]
                elif t_normalized.startswith("mcp_"):
                    t_normalized = t_normalized[4:]
                
                normalized_tools_map[t_normalized] = t_name
                # Also add the original name to support exact matches
                normalized_tools_map[t_name] = t_name
            
            # Now try to find a match for the tool name
            target_tool_name = tool_name
            normalized_input = tool_name
            
            # Normalize the input tool name
            if normalized_input.startswith("mcp0_"):
                normalized_input = normalized_input[5:]
            elif normalized_input.startswith("mcp_"):
                normalized_input = normalized_input[4:]
            
            # Look for the normalized name in our map
            if normalized_input in normalized_tools_map:
                target_tool_name = normalized_tools_map[normalized_input]
                logger.info(f"Matched tool name: {original_tool_name} -> {target_tool_name}")
            elif tool_name in normalized_tools_map:
                target_tool_name = normalized_tools_map[tool_name]
                logger.info(f"Exact match for tool name: {tool_name}")
            else:
                logger.warning(f"No matching tool found for: {original_tool_name}")
                # Continue with original name, which will likely fail
            
            # Execute the tool with the resolved name
            try:
                result = await execute_tool(target_tool_name, tool_parameters)
                
                # Send the result back
                if not is_notification:
                    # Format according to MCP spec
                    if isinstance(result, dict) and "isError" in result:
                        # Already formatted correctly
                        await send_jsonrpc_response(request_id, result)
                    else:
                        # Format as MCP tool result
                        formatted_result = {
                            "content": [
                                {
                                    "type": "text",
                                    "text": json.dumps(result)
                                }
                            ],
                            "isError": False
                        }
                        await send_jsonrpc_response(request_id, formatted_result)
            except Exception as e:
                logger.error(f"Error executing tool {tool_name}: {str(e)}")
                logger.error(traceback.format_exc())
                
                if not is_notification:
                    await send_jsonrpc_error(
                        request_id,
                        -32603,  # Internal error
                        f"Error executing tool: {str(e)}"
                    )
        
        elif method == "list_tools" or method == "tools/list":
            # Return the list of available tools
            logger.info(f"Received tools list request: {method}")
            
            # Get pagination parameters if present
            cursor = params.get("cursor", None)
            
            # In a real implementation, we would handle pagination here
            # For now, we return all tools at once
            
            if not is_notification:
                # Format response according to MCP spec
                await send_jsonrpc_response(request_id, {
                    "tools": TOOLS,
                    "nextCursor": None  # No more pages
                })
        
        else:
            # Unknown method
            logger.warning(f"Unknown method: {method}")
            
            if not is_notification:
                await send_jsonrpc_error(
                    request_id,
                    -32601,  # Method not found
                    f"Method not found: {method}"
                )
    except Exception as e:
        logger.error(f"Error handling JSON-RPC request: {str(e)}")
        logger.error(traceback.format_exc())
        
        if not is_notification:
            await send_jsonrpc_error(
                request_id,
                -32603,  # Internal error
                f"Internal error: {str(e)}"
            )

async def send_jsonrpc_response(request_id: Any, result: Any) -> None:
    """Send a JSON-RPC response
    
    Args:
        request_id: The ID of the request
        result: The result to send
    """
    response = {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": result
    }
    
    # Log the response for debugging
    logger.debug(f"Sending JSON-RPC response: id={request_id}")
    
    # Send the response through the transport
    transport._send_message(response)

async def send_jsonrpc_error(request_id: Any, code: int, message: str, data: Any = None) -> None:
    """Send a JSON-RPC error response
    
    Args:
        request_id: The ID of the request
        code: The error code
        message: The error message
        data: Additional error data
    """
    error = {
        "code": code,
        "message": message
    }
    
    if data is not None:
        error["data"] = data
        
    response = {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": error
    }
    
    # Log the error for debugging
    logger.error(f"Sending JSON-RPC error: id={request_id}, code={code}, message={message}")
    
    # Send the response through the transport
    transport._send_message(response)

async def main_loop() -> None:
    """Main event loop for the MCP server"""
    logger.info("Starting MCP server main loop")
    
    global transport
    transport = StdioTransport()
    transport.start()
    
    # Log server startup diagnostics
    logger.info(f"MCP server started with {len(TOOLS)} available tools")
    logger.info(f"Rate limiting {'enabled' if CONFIG['rate_limit']['enabled'] else 'disabled'}")
    
    try:
        # Send a notification that we're ready
        ready_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/server_ready",
            "params": {
                "timestamp": time.time()
            }
        }
        transport._send_message(ready_notification)
        
        # Process messages in a loop
        while True:
            try:
                # Wait for a message with a timeout
                message = transport.wait_for_message(timeout=1.0)
                
                if message:
                    # Process the message
                    await handle_jsonrpc_request(message)
                else:
                    # No message received in the timeout period
                    # This is normal, just continue the loop
                    await asyncio.sleep(0.01)  # Small sleep to reduce CPU usage
            except asyncio.CancelledError:
                logger.info("Main loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {str(e)}")
                logger.error(traceback.format_exc())
                await asyncio.sleep(0.1)  # Small sleep to avoid tight loop on error
    finally:
        # Clean up
        logger.info("Shutting down MCP server")
        transport.stop()

if __name__ == "__main__":
    # Register signal handlers for graceful shutdown
    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}, shutting down")
        sys.exit(0)
        
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Log startup information
    logger.info("Starting Build Together MCP Server")
    
    # Run the main loop
    asyncio.run(main_loop())
