#!/bin/bash

# Set environment variables
export PYTHONUNBUFFERED=1
export PYTHONIOENCODING=utf-8
export BTG_BASE_URL="http://127.0.0.1:3149"

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Create a lock file path
LOCK_FILE="$SCRIPT_DIR/.mcp_server.lock"

# Function to clean up before exit
cleanup() {
    echo "Cleaning up MCP server resources..."
    # Remove the lock file when the script exits
    if [ -f "$LOCK_FILE" ]; then
        rm "$LOCK_FILE"
    fi
    exit 0
}

# Set up trap to ensure cleanup happens on exit
trap cleanup EXIT INT TERM

# Check if the lock file exists (meaning another instance is running)
if [ -f "$LOCK_FILE" ]; then
    # Check if the process ID in the lock file is still running
    OLD_PID=$(cat "$LOCK_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "Another MCP server instance is already running with PID $OLD_PID"
        echo "If you believe this is an error, delete $LOCK_FILE and try again"
        exit 1
    else
        echo "Found stale lock file. Removing and continuing..."
        rm "$LOCK_FILE"
    fi
fi

# Create the lock file with our process ID
echo $$ > "$LOCK_FILE"

# Make sure we have the required dependencies
if [ ! -f venv/bin/activate ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Check if httpx is already installed to avoid unnecessary reinstallation
if ! pip show httpx > /dev/null 2>&1; then
    echo "Installing required httpx package..."
    pip install httpx > /dev/null 2>&1
fi

# Log startup information
echo "Starting MCP server with PID $$..."
echo "Lock file created at $LOCK_FILE"
echo "Current time: $(date)"

# Run the MCP server
# When run without arguments (by Windsurf), use stdio transport
python3 mcp_server.py "$@"
