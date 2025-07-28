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

# Check for system dependencies (Ubuntu/Debian)
check_system_deps() {
    if command_exists apt-get; then
        print_info "Detected Debian/Ubuntu system - checking for required system packages..."

        MISSING_PACKAGES=""

        # Check for libxml2-dev
        if ! dpkg -l | grep -q "libxml2-dev"; then
            MISSING_PACKAGES="$MISSING_PACKAGES libxml2-dev"
        fi

        # Check for libxslt1-dev
        if ! dpkg -l | grep -q "libxslt1-dev"; then
            MISSING_PACKAGES="$MISSING_PACKAGES libxslt1-dev"
        fi

        # Check for python3-dev
        if ! dpkg -l | grep -q "python3-dev"; then
            MISSING_PACKAGES="$MISSING_PACKAGES python3-dev"
        fi

        if [ ! -z "$MISSING_PACKAGES" ]; then
            print_warning "Missing system packages:$MISSING_PACKAGES"
            print_info "To install them, run:"
            print_info "sudo apt-get update && sudo apt-get install -y$MISSING_PACKAGES"
            echo ""
            read -p "Would you like to continue without these packages? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                print_info "Please install the system packages and run this script again."
                exit 1
            fi
        else
            print_success "All required system packages are installed ✓"
        fi
    elif command_exists yum; then
        print_info "Detected Red Hat/CentOS system - checking for required system packages..."
        print_warning "Make sure you have: libxml2-devel libxslt-devel python3-devel"
    elif command_exists pacman; then
        print_info "Detected Arch Linux system - checking for required system packages..."
        print_warning "Make sure you have: libxml2 libxslt python"
    elif command_exists brew; then
        print_info "Detected macOS with Homebrew - checking for required system packages..."
        if ! brew list libxml2 >/dev/null 2>&1; then
            print_info "Installing libxml2 via Homebrew..."
            brew install libxml2
        fi
        if ! brew list libxslt >/dev/null 2>&1; then
            print_info "Installing libxslt via Homebrew..."
            brew install libxslt
        fi
    else
        print_warning "Unknown package manager. Make sure libxml2 and libxslt development packages are installed."
    fi
}

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

# Check system dependencies
check_system_deps

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

    # Try to install with retry mechanism for network issues
    for i in {1..3}; do
        if pip install -r "$CRAWLER_DIR/requirements.txt"; then
            print_success "All dependencies installed successfully!"
            break
        else
            if [ $i -eq 3 ]; then
                print_error "Failed to install dependencies after 3 attempts."
                print_info "You may need to install system dependencies. See the error messages above."
                print_info "For Ubuntu/Debian: sudo apt-get install libxml2-dev libxslt1-dev python3-dev"
                print_info "For CentOS/RHEL: sudo yum install libxml2-devel libxslt-devel python3-devel"
                print_info "For macOS: brew install libxml2 libxslt"
                exit 1
            else
                print_warning "Installation failed, retrying... (attempt $i/3)"
                sleep 2
            fi
        fi
    done
else
    print_error "requirements.txt not found in $CRAWLER_DIR"
    exit 1
fi

# Verify installation
print_info "Verifying installation..."
python -c "import aiohttp, bs4, requests, selenium, pandas" 2>/dev/null
if [ $? -eq 0 ]; then
    print_success "Core dependencies are working correctly!"

    # Check optional dependencies
    python -c "import lxml" 2>/dev/null
    if [ $? -eq 0 ]; then
        print_success "lxml is working correctly! ✓"
    else
        print_warning "lxml is not available - using html5lib as fallback parser"
    fi
else
    print_warning "Some core dependencies may not be properly installed."
fi# Create .env file if it doesn't exist
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
