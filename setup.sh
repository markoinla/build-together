#!/bin/bash

# Build Together Setup Script
# This script sets up the Build Together application after cloning from GitHub

# Print colored output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Build Together Setup ===${NC}"
echo "This script will set up the Build Together application."
echo "It will create a virtual environment, install dependencies, and initialize the database."
echo ""

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check for Python 3.9+
echo -e "${YELLOW}Checking Python version...${NC}"
if command -v python3 &>/dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d '.' -f 1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d '.' -f 2)
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]); then
        echo -e "${RED}Error: Python 3.9 or higher is required. Found Python $PYTHON_VERSION${NC}"
        exit 1
    else
        echo -e "${GREEN}Found Python $PYTHON_VERSION${NC}"
    fi
else
    echo -e "${RED}Error: Python 3 not found. Please install Python 3.9 or higher.${NC}"
    exit 1
fi

# Check for pip
echo -e "${YELLOW}Checking pip...${NC}"
if ! command -v pip3 &>/dev/null; then
    echo -e "${RED}Error: pip3 not found. Please install pip for Python 3.${NC}"
    exit 1
else
    echo -e "${GREEN}Found pip3${NC}"
fi

# Create and activate virtual environment
echo -e "${YELLOW}Setting up Python virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}Created virtual environment${NC}"
else
    echo -e "${YELLOW}Virtual environment already exists${NC}"
fi

# Activate virtual environment
source venv/bin/activate
echo -e "${GREEN}Activated virtual environment${NC}"

# Install Python dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}Installed Python dependencies${NC}"

# Initialize the database
echo -e "${YELLOW}Initializing database...${NC}"
echo "This will create the database and add sample data."
read -p "Do you want to reset the database if it exists? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python init_db.py --reset
    echo -e "${GREEN}Database reset and initialized with sample data${NC}"
else
    python init_db.py
    echo -e "${GREEN}Database initialized (if it didn't exist) and sample data added${NC}"
fi

# Make MCP server script executable
echo -e "${YELLOW}Configuring MCP server...${NC}"
chmod +x mcp/run_mcp.sh
echo -e "${GREEN}Made MCP server script executable${NC}"

# Create a simple script to run the application
echo -e "${YELLOW}Creating run script...${NC}"
cat > run.sh << 'EOF'
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
EOF

chmod +x run.sh
echo -e "${GREEN}Created run script${NC}"

# Display setup completion message
echo ""
echo -e "${GREEN}=== Setup Complete ===${NC}"
echo "Build Together has been set up successfully!"
echo ""
echo "To run the application:"
echo "  1. Run './run.sh' to start the Flask application"
echo "  2. Access the application at http://127.0.0.1:3149 (or the port you configured)"
echo "  3. Optional: In a separate terminal, run './mcp/run_mcp.sh' to start the MCP server"
echo ""
echo "For MCP integration with Cursor or Windsurf:"
echo "  1. Configure Cursor or Windsurf to use the MCP server at: $(pwd)/mcp/run_mcp.sh"
echo ""
echo "Vibe something fun with Build Together!"