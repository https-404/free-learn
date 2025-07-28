#!/bin/bash

# install-crawler.sh - Setup script for the data crawler project
# This script creates a Python virtual environment and installs all dependencies

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if Python is installed
if ! command_exists python3; then
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    print_error "Python $PYTHON_VERSION is installed, but Python $REQUIRED_VERSION or higher is required."
    exit 1
fi

print_info "Python $PYTHON_VERSION detected ✓"

# Get the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CRAWLER_DIR="$PROJECT_ROOT/apps/data-crawler"
VENV_DIR="$PROJECT_ROOT/.venv"

print_info "Project root: $PROJECT_ROOT"
print_info "Crawler directory: $CRAWLER_DIR"
print_info "Virtual environment: $VENV_DIR"

# Check if we're in the right directory
if [ ! -f "$PROJECT_ROOT/package.json" ] || [ ! -f "$CRAWLER_DIR/main.py" ]; then
    print_error "This script must be run from the free-learn project root or scripts directory."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    print_info "Creating Python virtual environment..."
    python3 -m venv "$VENV_DIR"
    print_success "Virtual environment created at $VENV_DIR"
else
    print_warning "Virtual environment already exists at $VENV_DIR"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip
print_info "Upgrading pip..."
python -m pip install --upgrade pip

# Install requirements
if [ -f "$CRAWLER_DIR/requirements.txt" ]; then
    print_info "Installing Python dependencies..."
    pip install -r "$CRAWLER_DIR/requirements.txt"
    print_success "All dependencies installed successfully!"
else
    print_error "requirements.txt not found in $CRAWLER_DIR"
    exit 1
fi

# Verify installation
print_info "Verifying installation..."
python -c "import aiohttp, beautifulsoup4, requests, selenium, lxml, pandas" 2>/dev/null
if [ $? -eq 0 ]; then
    print_success "All main dependencies are working correctly!"
else
    print_warning "Some dependencies may not be properly installed."
fi

# Create .env file if it doesn't exist
ENV_FILE="$CRAWLER_DIR/.env"
if [ ! -f "$ENV_FILE" ]; then
    print_info "Creating sample .env file..."
    cat > "$ENV_FILE" << EOF
# Crawler Configuration
CRAWLER_LOG_LEVEL=INFO
CRAWLER_OUTPUT_DIR=./output
CRAWLER_RATE_LIMIT=1
CRAWLER_USER_AGENT=FreeLearn-Crawler/1.0

# Optional: API Keys (uncomment and add your keys as needed)
# YOUTUBE_API_KEY=your_youtube_api_key_here
# COURSERA_API_KEY=your_coursera_api_key_here
EOF
    print_success "Created sample .env file at $ENV_FILE"
fi

# Test the crawler
print_info "Testing crawler setup..."
cd "$CRAWLER_DIR"
if python main.py --help >/dev/null 2>&1; then
    print_success "Crawler is ready to use!"
    echo ""
    print_info "To run the crawler:"
    echo "  cd apps/data-crawler"
    echo "  source ../../.venv/bin/activate"
    echo "  python main.py \"computer science\" --limit 5"
    echo ""
    print_info "Or use Nx commands:"
    echo "  pnpm start:crawler:example"
    echo "  nx run data-crawler:run"
else
    print_warning "Crawler test failed, but dependencies are installed."
fi

print_success "Setup completed successfully!"
print_info "Virtual environment is located at: $VENV_DIR"
print_info "To activate it manually: source $VENV_DIR/bin/activate"
