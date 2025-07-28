# Scripts Directory

This directory contains setup and utility scripts for the Free Learn project.

## Available Scripts

### `install-crawler.sh` (Linux/macOS)

Sets up the Python virtual environment and installs all dependencies for the data crawler.

**Usage:**

```bash
# From project root
./scripts/install-crawler.sh

# Or via npm/pnpm
pnpm setup:crawler
```

**Features:**

- Creates a `.venv` directory in the project root
- Installs all Python dependencies from `requirements.txt`
- Checks for required system dependencies
- Creates a sample `.env` file
- Verifies the installation
- Provides helpful usage instructions

**System Requirements:**

- Python 3.8 or higher
- For full functionality (lxml support):
  - **Ubuntu/Debian**: `sudo apt-get install libxml2-dev libxslt1-dev python3-dev`
  - **CentOS/RHEL**: `sudo yum install libxml2-devel libxslt-devel python3-devel`
  - **Arch Linux**: `sudo pacman -S libxml2 libxslt python`
  - **macOS**: `brew install libxml2 libxslt`

### `install-crawler.ps1` (Windows)

PowerShell version of the installation script for Windows users.

**Usage:**

```powershell
# From project root
.\scripts\install-crawler.ps1

# Force reinstall
.\scripts\install-crawler.ps1 -Force
```

## Troubleshooting

### lxml Installation Issues

If you encounter issues installing lxml (common on some systems), the script will:

1. **First attempt**: Install full requirements including lxml
2. **Fallback**: Use html5lib as an alternative parser
3. **Manual fix**: Follow the system-specific instructions provided

### Common Solutions

**Ubuntu/Debian:**

```bash
sudo apt-get update
sudo apt-get install libxml2-dev libxslt1-dev python3-dev build-essential
```

**CentOS/RHEL:**

```bash
sudo yum install libxml2-devel libxslt-devel python3-devel gcc
```

**macOS:**

```bash
# If using Homebrew
brew install libxml2 libxslt

# If using MacPorts
sudo port install libxml2 libxslt
```

**Windows:**

```powershell
# lxml should install without issues on Windows
# If problems persist, ensure Visual Studio Build Tools are installed
```

### Virtual Environment Issues

If you need to recreate the virtual environment:

```bash
# Remove existing environment
rm -rf .venv

# Run setup script again
./scripts/install-crawler.sh
```

### Permission Issues

Make sure the script is executable:

```bash
chmod +x scripts/install-crawler.sh
```

## Script Details

### What the Script Does

1. **Environment Check**: Verifies Python version and system compatibility
2. **System Dependencies**: Checks for required development libraries
3. **Virtual Environment**: Creates `.venv` in project root
4. **Package Installation**: Installs all Python dependencies
5. **Configuration**: Creates sample `.env` file with default settings
6. **Verification**: Tests that key packages can be imported
7. **Usage Guide**: Provides next steps and usage examples

### Generated Files

After running the script, you'll have:

- `.venv/` - Python virtual environment
- `apps/data-crawler/.env` - Environment configuration file
- All Python packages installed and ready to use

### Environment Variables

The script creates a `.env` file with these defaults:

```env
CRAWLER_LOG_LEVEL=INFO
CRAWLER_OUTPUT_DIR=./output
CRAWLER_RATE_LIMIT=1
CRAWLER_USER_AGENT=FreeLearn-Crawler/1.0
```

You can modify these values as needed for your use case.

## Integration with Package Scripts

The installation script is integrated with the project's package.json:

```json
{
  "scripts": {
    "setup:crawler": "./scripts/install-crawler.sh"
  }
}
```

This allows you to run the setup from anywhere in the project using:

```bash
pnpm setup:crawler
# or
npm run setup:crawler
```
