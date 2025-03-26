#!/bin/bash
# Script to run the Build Together application

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment
source venv/bin/activate

# Get port from config
PORT=$(python -c "from config import Config; print(Config.PORT)")

# Run the Flask application
echo "Starting Build Together on http://127.0.0.1:$PORT"
flask run --port $PORT
