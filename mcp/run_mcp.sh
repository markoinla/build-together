#!/bin/bash

# Redirect all output to stderr by default
exec 3>&1  # Save original stdout to file descriptor 3
exec 1>&2  # Redirect stdout to stderr

# Parse command line arguments
PORT=3149  # Default port
AUTO_START=true  # Default to auto-start Build Together

# First argument is PORT
if [ $# -gt 0 ]; then
    PORT=$1
fi

# Second argument is AUTO_START
if [ $# -gt 1 ]; then
    AUTO_START=$2
fi

# Change to the project root directory
cd "$(dirname "$0")/.."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Check if Build Together is already running on the specified port
echo "Checking if Build Together is running on port $PORT..."
if curl -s "http://localhost:$PORT/api/projects" > /dev/null; then
    echo "Build Together is already running on port $PORT"
elif [ "$AUTO_START" = "true" ]; then
    echo "Build Together is not running on port $PORT, starting it now..."
    # Start Build Together in the background
    ./run.sh &
    
    # Wait for server to start
    echo "Waiting for Build Together to start..."
    for i in {1..10}; do
        if curl -s "http://localhost:$PORT/api/projects" > /dev/null; then
            echo "Build Together started successfully on port $PORT"
            break
        fi
        if [ $i -eq 10 ]; then
            echo "Warning: Couldn't confirm Build Together started. Will proceed anyway..."
        fi
        sleep 1
    done
else
    echo "Build Together is not running on port $PORT and auto-start is disabled."
    echo "The MCP server will still start, but commands will fail until Build Together is running."
fi

# Run the MCP server
echo "Starting Build Together MCP server (connecting to port $PORT)..."
# Restore stdout for the Python process (so it can write JSON to stdout)
exec 1>&3

# Run the Python script, redirecting stderr to our stderr (fd 2)
python mcp/build_together_mcp.py --port $PORT 2>&2

# Deactivate virtual environment on exit
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi 