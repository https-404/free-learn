# install-crawler.ps1 - Setup script for the data crawler project (Windows)
# This script creates a Python virtual environment and installs all dependencies

param(
    [switch]$Force = $false
)

# Colors for output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Cyan"

function Write-Info {
    param($Message)
    Write-Host "[INFO] $Message" -ForegroundColor $Blue
}

function Write-Success {
    param($Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor $Green
}

function Write-Warning {
    param($Message)
    Write-Host "[WARNING] $Message" -ForegroundColor $Yellow
}

function Write-Error {
    param($Message)
    Write-Host "[ERROR] $Message" -ForegroundColor $Red
}

# Function to check if command exists
function Test-Command {
    param($Command)
    $null = Get-Command $Command -ErrorAction SilentlyContinue
    return $?
}

# Check if Python is installed
if (-not (Test-Command "python")) {
    Write-Error "Python is not installed or not in PATH. Please install Python 3.8 or higher."
    exit 1
}

# Check Python version
try {
    $pythonVersion = python -c "import sys; print('.'.join(map(str, sys.version_info[:2])))"
    $requiredVersion = [Version]"3.8"
    $currentVersion = [Version]$pythonVersion

    if ($currentVersion -lt $requiredVersion) {
        Write-Error "Python $pythonVersion is installed, but Python 3.8 or higher is required."
        exit 1
    }

    Write-Info "Python $pythonVersion detected ✓"
} catch {
    Write-Error "Failed to check Python version."
    exit 1
}

# Get directories
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$CrawlerDir = Join-Path $ProjectRoot "apps\data-crawler"
$VenvDir = Join-Path $ProjectRoot ".venv"

Write-Info "Project root: $ProjectRoot"
Write-Info "Crawler directory: $CrawlerDir"
Write-Info "Virtual environment: $VenvDir"

# Check if we're in the right directory
$PackageJsonPath = Join-Path $ProjectRoot "package.json"
$MainPyPath = Join-Path $CrawlerDir "main.py"

if (-not (Test-Path $PackageJsonPath) -or -not (Test-Path $MainPyPath)) {
    Write-Error "This script must be run from the free-learn project root or scripts directory."
    exit 1
}

# Create virtual environment if it doesn't exist
if (-not (Test-Path $VenvDir) -or $Force) {
    if ($Force -and (Test-Path $VenvDir)) {
        Write-Info "Removing existing virtual environment..."
        Remove-Item -Recurse -Force $VenvDir
    }

    Write-Info "Creating Python virtual environment..."
    python -m venv $VenvDir
    Write-Success "Virtual environment created at $VenvDir"
} else {
    Write-Warning "Virtual environment already exists at $VenvDir"
}

# Activate virtual environment
Write-Info "Activating virtual environment..."
$ActivateScript = Join-Path $VenvDir "Scripts\Activate.ps1"

if (Test-Path $ActivateScript) {
    & $ActivateScript
} else {
    Write-Error "Failed to find activation script at $ActivateScript"
    exit 1
}

# Upgrade pip
Write-Info "Upgrading pip..."
python -m pip install --upgrade pip

# Install requirements
$RequirementsPath = Join-Path $CrawlerDir "requirements.txt"
if (Test-Path $RequirementsPath) {
    Write-Info "Installing Python dependencies..."
    pip install -r $RequirementsPath
    Write-Success "All dependencies installed successfully!"
} else {
    Write-Error "requirements.txt not found in $CrawlerDir"
    exit 1
}

# Verify installation
Write-Info "Verifying installation..."
try {
    python -c "import aiohttp, beautifulsoup4, requests, selenium, lxml, pandas" 2>$null
    Write-Success "All main dependencies are working correctly!"
} catch {
    Write-Warning "Some dependencies may not be properly installed."
}

# Create .env file if it doesn't exist
$EnvFile = Join-Path $CrawlerDir ".env"
if (-not (Test-Path $EnvFile)) {
    Write-Info "Creating sample .env file..."
    @"
# Crawler Configuration
CRAWLER_LOG_LEVEL=INFO
CRAWLER_OUTPUT_DIR=./output
CRAWLER_RATE_LIMIT=1
CRAWLER_USER_AGENT=FreeLearn-Crawler/1.0

# Optional: API Keys (uncomment and add your keys as needed)
# YOUTUBE_API_KEY=your_youtube_api_key_here
# COURSERA_API_KEY=your_coursera_api_key_here
"@ | Out-File -FilePath $EnvFile -Encoding UTF8
    Write-Success "Created sample .env file at $EnvFile"
}

# Test the crawler
Write-Info "Testing crawler setup..."
Push-Location $CrawlerDir
try {
    $null = python main.py --help 2>$null
    Write-Success "Crawler is ready to use!"
    Write-Host ""
    Write-Info "To run the crawler:"
    Write-Host "  cd apps\data-crawler"
    Write-Host "  .\.venv\Scripts\Activate.ps1"
    Write-Host "  python main.py `"computer science`" --limit 5"
    Write-Host ""
    Write-Info "Or use npm/pnpm commands:"
    Write-Host "  pnpm setup:crawler"
    Write-Host "  pnpm start:crawler:example"
} catch {
    Write-Warning "Crawler test failed, but dependencies are installed."
} finally {
    Pop-Location
}

Write-Success "Setup completed successfully!"
Write-Info "Virtual environment is located at: $VenvDir"
Write-Info "To activate it manually: $VenvDir\Scripts\Activate.ps1"
